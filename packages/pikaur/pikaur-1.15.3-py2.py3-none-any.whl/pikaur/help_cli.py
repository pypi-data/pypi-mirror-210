"""Licensed under GPLv3, see https://www.gnu.org/licenses/"""
from typing import TYPE_CHECKING

from .args import LiteralArgs, get_pikaur_long_opts, parse_args, reconstruct_args
from .config import PikaurConfig
from .core import spawn
from .i18n import PIKAUR_NAME, translate
from .pprint import print_stdout

if TYPE_CHECKING:
    from typing import Final

FIRST_COLUMN_MARGIN: "Final" = 5
FIRST_COLUMN_WIDTH: "Final" = 16


def _format_options_help(options: list[tuple[str, str, str]]) -> str:
    return "\n".join([
        "{:>{first_column_margin}} {:<{first_column_width}} {}".format(
            short_opt and (short_opt + ",") or "",
            long_opt or "",
            descr if (
                (len(short_opt) + len(long_opt)) < FIRST_COLUMN_WIDTH
            ) else f"\n{(FIRST_COLUMN_MARGIN + FIRST_COLUMN_WIDTH + 2) * ' '}{descr}",
            first_column_margin=FIRST_COLUMN_MARGIN,
            first_column_width=FIRST_COLUMN_WIDTH,
        )
        for short_opt, long_opt, descr in options
    ])


def cli_print_help() -> None:
    args = parse_args()

    proc = spawn([
        PikaurConfig().misc.PacmanPath.get_str(),
        *reconstruct_args(args, ignore_args=get_pikaur_long_opts()),
    ])
    if not proc.stdout_text:
        no_response_from_pacman = translate("No response from Pacman")
        raise RuntimeError(no_response_from_pacman)
    pacman_help = proc.stdout_text.replace(
        "pacman", PIKAUR_NAME,
    ).replace(
        "options:", "\n" + translate("Common pacman options:"),
    )
    if LiteralArgs.HELP in pacman_help:
        pacman_help += (
            "\n" +
            translate("pikaur-specific operations:") + "\n    " +
            translate("pikaur {-P --pkgbuild}    [options] [file(s)]") + "\n    " +
            translate("pikaur {-G --getpkgbuild} [options] <package(s)>")
        )
    if args.pkgbuild:
        pacman_help = (
            translate("usage:  pikaur {-P --pkgbuild} [options] <file(s)>") + "\n\n" +
            translate(
                "All common pacman options as when doing `pacman -U <pkg_file>`. See `pacman -Uh`.",
            )
        )
    if args.getpkgbuild:
        pacman_help = (
            translate("usage:  pikaur {-G --getpkgbuild} [options] <package(s)>")
        )

    pikaur_options_help: list[tuple[str, str, str]] = []
    if args.getpkgbuild:
        pikaur_options_help += [
            ("-d", "--deps", translate("download also AUR dependencies")),
        ]
    if args.pkgbuild:
        pikaur_options_help += [
            ("-i", "--install", translate("install built package")),
        ]
    if args.sync or args.query or args.pkgbuild:
        pikaur_options_help += [
            ("-a", "--aur", translate("query packages from AUR only")),
        ]
    if args.query:
        pikaur_options_help += [
            ("", "--repo", translate("query packages from repository only")),
        ]
    if args.sync or args.pkgbuild:
        pikaur_options_help += [
            ("-o", "--repo", translate("query packages from repository only")),
            ("", "--noedit", translate("don't prompt to edit PKGBUILDs and other build files")),
            ("", "--edit", translate("prompt to edit PKGBUILDs and other build files")),
            ("-k", "--keepbuild", translate("don't remove build dir after the build")),
            ("", "--rebuild", translate("always rebuild AUR packages")),
            ("", "--mflags=<--flag1>,<--flag2>", translate("cli args to pass to makepkg")),
            ("", "--makepkg-config=<path>", translate("path to custom makepkg config")),
            ("", "--makepkg-path=<path>", translate("override path to makepkg executable")),
            ("", "--pikaur-config=<path>", translate("path to custom pikaur config")),
            ("", "--dynamic-users", translate("always isolate with systemd dynamic users")),
            ("", "--build-gpgdir=<path>",
                translate("set GnuPG home directory used when validating package sources")),
            ("", "--skip-failed-build", translate("skip failed builds")),
            ("", "--hide-build-log", translate("hide build log")),
            ("", "--skip-aur-pull", translate("don't pull already cloned PKGBUILD")),
            ("", "--aur-clone-concurrency", translate("how many git-clones/pulls to do from AUR")),
        ]
    if args.sync:
        pikaur_options_help += [
            ("", "--namesonly", translate("search only in package names")),
            ("", "--devel", translate("always sysupgrade '-git', '-svn' and other dev packages")),
            ("", "--nodiff", translate("don't prompt to show the build files diff")),
            ("", "--ignore-outofdate", translate(
                "ignore AUR packages' updates which marked 'outofdate'",
            )),
        ]

    if pikaur_options_help:  # if it's not just `pikaur --help`
        pikaur_options_help += [
            ("", "--print-commands", translate("print spawned by pikaur subshell commands")),
            ("", "--pikaur-debug", translate("show only debug messages specific to pikaur")),
        ]

    print_stdout("".join([
        pacman_help,
        "\n\n" + translate("Pikaur-specific options:") + "\n" if pikaur_options_help else "",
        _format_options_help(pikaur_options_help),
    ]))
