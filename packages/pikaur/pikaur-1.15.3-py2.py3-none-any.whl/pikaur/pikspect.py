"""Licensed under GPLv3, see https://www.gnu.org/licenses/"""

import contextlib
import fcntl
import os
import pty
import re
import select
import shutil
import signal
import struct
import subprocess  # nosec B404
import sys
import termios
import tty
from multiprocessing.pool import ThreadPool
from pathlib import Path
from time import sleep
from typing import TYPE_CHECKING

from .args import parse_args
from .config import PikaurConfig
from .core import DEFAULT_INPUT_ENCODING, get_sudo_refresh_command
from .i18n import translate
from .logging import create_logger
from .pacman_i18n import _p
from .pprint import (
    ColorsHighlight,
    PrintLock,
    bold_line,
    color_line,
    get_term_width,
    print_stderr,
)

if TYPE_CHECKING:
    from collections.abc import Callable
    from typing import Any, BinaryIO, Final, TextIO


SMALL_TIMEOUT: "Final" = 0.01


TcAttrsType = list[int | list[bytes | int]]


logger = create_logger("pikspect", lock=False)


class ReadlineKeycodes:
    CTRL_C: "Final" = 3
    CTRL_D: "Final" = 4
    CTRL_W: "Final" = 23
    ENTER: "Final" = 13
    BACKSPACE: "Final" = 127


class TTYRestore():  # pragma: no cover

    old_tcattrs = None
    old_tcattrs_out = None
    old_tcattrs_err = None
    sub_tty_old_tcattrs = None
    sub_tty_old_tcattrs_out = None
    sub_tty_old_tcattrs_err = None

    @classmethod
    def save(cls) -> None:
        if sys.stdin.isatty():
            cls.old_tcattrs = termios.tcgetattr(sys.stdin.fileno())
        if sys.stdout.isatty():
            cls.old_tcattrs_out = termios.tcgetattr(sys.stdout.fileno())
        if sys.stderr.isatty():
            cls.old_tcattrs_err = termios.tcgetattr(sys.stderr.fileno())

    @classmethod
    def _restore(
            cls,
            what: TcAttrsType | None = None,
            what_out: TcAttrsType | None = None,
            what_err: TcAttrsType | None = None,
    ) -> None:
        # if sys.stdout.isatty():
        #     termios.tcdrain(sys.stdout.fileno())
        # if sys.stderr.isatty():
        #     termios.tcdrain(sys.stderr.fileno())
        # if sys.stdin.isatty():
        #     termios.tcflush(sys.stdin.fileno(), termios.TCIOFLUSH)
        if what:
            try:
                termios.tcsetattr(sys.stdin.fileno(), termios.TCSANOW, what)
            except termios.error as exc:
                logger.debug(",".join(str(arg) for arg in exc.args))
        if what_out:
            try:
                termios.tcsetattr(sys.stdout.fileno(), termios.TCSANOW, what_out)
            except termios.error as exc:
                logger.debug(",".join(str(arg) for arg in exc.args))
        if what_err:
            try:
                termios.tcsetattr(sys.stderr.fileno(), termios.TCSANOW, what_err)
            except termios.error as exc:
                logger.debug(",".join(str(arg) for arg in exc.args))

    @classmethod
    def restore(cls, *_whatever: "Any") -> None:
        cls._restore(cls.old_tcattrs, cls.old_tcattrs_out, cls.old_tcattrs_err)

    def __init__(self) -> None:
        with contextlib.suppress(termios.error, ValueError):
            self.sub_tty_old_tcattrs = termios.tcgetattr(sys.stdin.fileno())
        with contextlib.suppress(termios.error):
            self.sub_tty_old_tcattrs_out = termios.tcgetattr(sys.stdout.fileno())
        with contextlib.suppress(termios.error):
            self.sub_tty_old_tcattrs_err = termios.tcgetattr(sys.stderr.fileno())

    def restore_new(self, *_whatever: "Any") -> None:
        self._restore(
            self.sub_tty_old_tcattrs, self.sub_tty_old_tcattrs_out, self.sub_tty_old_tcattrs_err,
        )


TTYRestore.save()


def set_terminal_geometry(file_descriptor: int, rows: int, columns: int) -> None:
    term_geometry_struct = struct.pack("HHHH", rows, columns, 0, 0)
    fcntl.ioctl(
        file_descriptor, termios.TIOCSWINSZ, term_geometry_struct,
    )


class TTYInputWrapper():  # pragma: no cover

    tty_opened = False

    def __init__(self) -> None:
        self.is_pipe = not sys.stdin.isatty()

    def __enter__(self) -> None:
        if self.is_pipe:
            self.old_stdin = sys.stdin
            try:
                logger.debug("Attaching to TTY manually...")
                sys.stdin = Path("/dev/tty").open(encoding=DEFAULT_INPUT_ENCODING)
                self.tty_opened = True
            except Exception as exc:
                logger.debug(exc)

    def __exit__(self, *_exc_details: "Any") -> None:
        if self.is_pipe and self.tty_opened:
            logger.debug("Restoring stdin...", lock=False)
            sys.stdin.close()
            sys.stdin = self.old_stdin


class NestedTerminal():

    def __init__(self) -> None:
        self.tty_wrapper = TTYInputWrapper()

    def __enter__(self) -> os.terminal_size:
        logger.debug("Opening virtual terminal...")
        self.tty_wrapper.__enter__()
        real_term_geometry = shutil.get_terminal_size((80, 80))
        for stream in (
                sys.stdin,
                sys.stderr,
                sys.stdout,
        ):
            if stream.isatty():
                tty.setcbreak(stream.fileno())
        return real_term_geometry

    def __exit__(self, *exc_details: "Any") -> None:
        self.tty_wrapper.__exit__(*exc_details)
        TTYRestore.restore()


RECOGNIZED_REGEX_SEQUENCES: "Final[tuple[str]]" = (".*", )


def _match(pattern: str, line: str) -> bool:
    return len(line) >= len(pattern) and bool(
        re.compile(pattern).search(line)
        if max(sequence in pattern for sequence in RECOGNIZED_REGEX_SEQUENCES) else
        (pattern in line),
    )


class PikspectSignalHandler():

    signal_handler: "Callable[..., Any] | None" = None

    @classmethod
    def set_handler(cls, signal_handler: "Callable[..., Any]") -> None:
        cls.signal_handler = signal_handler

    @classmethod
    def clear(cls) -> None:
        cls.signal_handler = None

    @classmethod
    def get(cls) -> "Callable[..., Any] | None":
        return cls.signal_handler


class PikspectPopen(subprocess.Popen[bytes]):

    print_output: bool
    capture_input: bool
    capture_output: bool
    historic_output: list[bytes]
    pty_in: "TextIO"
    pty_out: "BinaryIO"
    default_questions: dict[str, list[str]]
    # max_question_length = 0  # preserve enough information to analyze questions
    max_question_length = get_term_width() * 2  # preserve also at least last line
    # write buffer:
    _write_buffer: bytes = b""
    # some help for mypy:
    output: bytes = b""

    def __init__(
            self,
            args: list[str],
            *,
            print_output: bool = True,
            capture_input: bool = True,
            capture_output: bool = False,
            default_questions: dict[str, list[str]] | None = None,
    ) -> None:
        self.args = args
        self.print_output = print_output
        self.capture_input = capture_input
        self.capture_output = capture_output
        self.default_questions = {}
        self.historic_output = []
        if default_questions:
            self.add_answers(default_questions)

        self.pty_user_master, self.pty_user_slave = pty.openpty()
        self.pty_cmd_master, self.pty_cmd_slave = pty.openpty()

        super().__init__(
            args=args,
            stdin=self.pty_user_slave,
            stdout=self.pty_cmd_slave,
            stderr=self.pty_cmd_slave,
        )

    def __del__(self) -> None:
        self.terminate()
        self.communicate()

    def add_answers(self, extra_questions: dict[str, list[str]]) -> None:
        for answer, questions in extra_questions.items():
            self.default_questions[answer] = self.default_questions.get(answer, []) + questions
            for question in questions:
                if len(question) > self.max_question_length:
                    self.max_question_length = len(question.encode(DEFAULT_INPUT_ENCODING))
        self.check_questions()

    def communicator_thread(self) -> int:
        result: int = self._wait(None)  # type: ignore[attr-defined]
        return result

    def run(self) -> None:
        if not isinstance(self.args, list):
            not_a_list_error = translate(
                "`{var_name}` should be list.",
            ).format(var_name="args")
            raise TypeError(not_a_list_error)
        PikspectSignalHandler.set_handler(
            lambda *_whatever: self.send_signal(signal.SIGINT),
        )
        try:
            with NestedTerminal() as real_term_geometry:

                if (
                        PikaurConfig().misc.PrivilegeEscalationTool.get_str() in self.args
                ):  # pragma: no cover
                    subprocess.run(  # nosec B603
                        get_sudo_refresh_command(),  # noqa: S603
                        check=True,
                    )
                with (
                        open(  # noqa: PTH123
                            self.pty_user_master, "w", encoding=DEFAULT_INPUT_ENCODING,
                        ) as self.pty_in,
                        open(  # noqa: PTH123
                            self.pty_cmd_master, "rb", buffering=0,
                        ) as self.pty_out,
                ):
                    set_terminal_geometry(
                        self.pty_out.fileno(),
                        columns=real_term_geometry.columns,
                        rows=real_term_geometry.lines,
                    )
                    with ThreadPool(processes=3) as pool:
                        output_task = pool.apply_async(self.cmd_output_reader_thread, ())
                        input_task = pool.apply_async(self.user_input_reader_thread, ())
                        communicate_task = pool.apply_async(self.communicator_thread, ())
                        pool.close()

                        output_task.get()
                        sys.stdout.buffer.write(self._write_buffer)
                        sys.stdout.buffer.flush()
                        communicate_task.get()
                        input_task.get()
                        pool.join()
        finally:
            PikspectSignalHandler.clear()
            os.close(self.pty_cmd_slave)
            os.close(self.pty_user_slave)

    def check_questions(self) -> None:
        try:
            historic_output = b"".join(self.historic_output).decode(DEFAULT_INPUT_ENCODING)
        except UnicodeDecodeError:  # pragma: no cover
            return

        clear_buffer = False

        for answer, questions in self.default_questions.items():
            for question in questions:
                if not _match(question, historic_output):
                    continue
                self.write_something((answer + "\n").encode(DEFAULT_INPUT_ENCODING))
                with PrintLock():
                    self.pty_in.write(answer)
                    sleep(SMALL_TIMEOUT)
                    self.pty_in.write("\n")
                    self.pty_in.flush()
                clear_buffer = True
                break

        if clear_buffer:
            self.historic_output = [b""]

    def write_buffer_contents(self) -> None:
        if self._write_buffer:
            sys.stdout.buffer.write(self._write_buffer)
            sys.stdout.buffer.flush()
            self._write_buffer = b""

    def write_something(self, output: bytes) -> None:
        if not (self.print_output or self.capture_output):
            return
        with PrintLock():
            if self.capture_output:
                self.output += output
            self._write_buffer += output
            self.write_buffer_contents()

    def cmd_output_reader_thread(self) -> None:
        while True:

            try:
                selected = select.select([self.pty_out], [], [], SMALL_TIMEOUT)
            except ValueError:  # pragma: no cover
                return
            readers = selected[0]
            if not readers:
                if self.returncode is not None:
                    break
                if not self.historic_output:
                    sleep(SMALL_TIMEOUT)
                self.write_buffer_contents()
                continue
            pty_reader = readers[0]
            output = pty_reader.read(4096)

            self.historic_output = (
                self.historic_output[-self.max_question_length:] + [output]
            )
            self.write_something(output)
            self.check_questions()

    def user_input_reader_thread(self) -> None:  # pragma: no cover
        while self.returncode is None:
            if not self.capture_input:
                sleep(SMALL_TIMEOUT)
                continue

            char = None

            if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
                char = sys.stdin.read(1)
                if char in [None, ""]:
                    sleep(SMALL_TIMEOUT)
                    continue
            else:
                sleep(SMALL_TIMEOUT)
                continue

            try:
                with PrintLock():
                    if ord(char) == ReadlineKeycodes.BACKSPACE:
                        sys.stdout.write("\b \b")
                    elif ord(char) == ReadlineKeycodes.CTRL_W:
                        sys.stdout.write(
                            "\r" + " " * get_term_width() + "\r" +
                            b"".join(
                                self.historic_output,
                            ).decode(DEFAULT_INPUT_ENCODING).splitlines()[-1],
                        )
                    self.pty_in.write(char)
                    self.pty_in.flush()
            except ValueError as exc:
                print(exc)  # noqa: T201
            self.write_something(char.encode(DEFAULT_INPUT_ENCODING))


class YesNo:
    ANSWER_Y = _p("Y")
    ANSWER_N = _p("N")
    QUESTION_YN_YES = _p("[Y/n]")
    QUESTION_YN_NO = _p("[y/N]")


def format_pacman_question(message: str, question: str = YesNo.QUESTION_YN_YES) -> str:
    return bold_line(f" {_p(message)} {question} ")


def pikspect(
        cmd: list[str],
        *,
        print_output: bool = True,
        auto_proceed: bool = True,
        conflicts: list[list[str]] | None = None,
        extra_questions: dict[str, list[str]] | None = None,
        capture_output: bool | None = None,
) -> PikspectPopen:

    class Questions:
        PROCEED = [
            format_pacman_question("Proceed with installation?"),
            format_pacman_question("Proceed with download?"),
        ]
        REMOVE = [
            format_pacman_question("Do you want to remove these packages?"),
        ]
        CONFLICT = format_pacman_question(
            "%s and %s are in conflict. Remove %s?", YesNo.QUESTION_YN_NO,
        )
        CONFLICT_VIA_PROVIDED = format_pacman_question(
            "%s and %s are in conflict (%s). Remove %s?", YesNo.QUESTION_YN_NO,
        )

    def format_conflicts(conflicts: list[list[str]]) -> list[str]:
        return [
            Questions.CONFLICT % (new_pkg, old_pkg, old_pkg)
            for new_pkg, old_pkg in conflicts
        ] + [
            (
                re.escape(Questions.CONFLICT_VIA_PROVIDED % (
                    new_pkg, old_pkg, ".*", old_pkg,
                ))
            ).replace(r"\.\*", ".*")
            for new_pkg, old_pkg in conflicts
        ]

    default_questions: dict[str, list[str]] = {}
    if auto_proceed:
        default_questions = {
            YesNo.ANSWER_Y: Questions.PROCEED + Questions.REMOVE,
            YesNo.ANSWER_N: [],
        }

    with PikspectPopen(
        cmd,
        print_output=print_output,
        default_questions=default_questions,
        capture_output=bool(capture_output),
    ) as proc:

        extra_questions = extra_questions or {}
        if conflicts:
            extra_questions[YesNo.ANSWER_Y] = (
                extra_questions.get(YesNo.ANSWER_Y, []) + format_conflicts(conflicts)
            )
        if extra_questions:
            proc.add_answers(extra_questions)

        if parse_args().print_commands:
            print_stderr(
                color_line("pikspect => ", ColorsHighlight.cyan) +
                " ".join(cmd),
            )
        proc.run()
        return proc


if __name__ == "__main__":
    pikspect(sys.argv[1:])
