"""The command line interface for PyGitViz."""
import time
import tempfile
import argparse
import sys
import logging
import contextlib
from pathlib import Path

import daiquiri

from _pygitviz import graphviz
from _pygitviz import util
from _pygitviz import git

daiquiri.setup(
    level=logging.WARNING,
    outputs=(
        daiquiri.output.Stream(
            sys.stdout,
            formatter=daiquiri.formatter.ColorFormatter(
                fmt="%(color)s[%(levelname)s] %(message)s%(color_stop)s"
            ),
        ),
    ),
)
LOGGER = daiquiri.getLogger(__file__)


def main() -> None:
    """Run the PyGitViz program."""
    operating_system = util.get_os()
    parser = _create_parser(operating_system)
    args = parser.parse_args(sys.argv[1:])

    with _convert_error_to_log(traceback=args.traceback):
        _validate_args(args)

        pdf_name = "graph.pdf"
        dot_name = "graph.dot"
        git_root = args.git_directory
        with tempfile.TemporaryDirectory() as tmpdir:
            dot_file = Path(str(tmpdir)) / dot_name
            pdf_file = Path(str(tmpdir)) / pdf_name
            _mainloop(
                git_root,
                dot_file,
                pdf_file,
                args.pdf_viewer,
                operating_system,
                args.hide_content,
            )


@contextlib.contextmanager
def _convert_error_to_log(traceback: bool):
    try:
        yield
    except KeyboardInterrupt:
        print("Exiting ...")
        sys.exit(0)
    except Exception as exc:
        if traceback:
            LOGGER.exception("Critical error, traceback follows")
        else:
            LOGGER.error(str(exc))
        sys.exit(1)


def _validate_args(args: argparse.Namespace) -> None:
    if not args.git_directory.is_dir():
        raise ValueError(
            f"no such directory: {args.git_directory}, please specify an "
            "existing .git directory with `--git-directory`"
        )


def _create_parser(operating_system: util.OS) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="PyGitViz",
        description="Git repository visualizer for education and demonstration purposes",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "-g",
        "--git-directory",
        help="Path to a .git directory",
        default=Path(".git"),
        type=Path,
    )
    parser.add_argument(
        "--hide-content",
        help=(
            "Hide trees and blobs from the representation, so only commits and "
            "refs are shown"
        ),
        action="store_true",
    )
    parser.add_argument(
        "-p",
        "--pdf-viewer",
        help="Program to open the resulting PDF file with",
        default=operating_system.open_pdf_cmd,
        type=str,
    )
    parser.add_argument(
        "--tb",
        "--traceback",
        dest="traceback",
        help="Show full traceback for critical errors",
        action="store_true",
    )
    return parser


def _create_graph_pdf(
    dot_file: Path, pdf_file: Path, git_root: Path, hide_content: bool
) -> None:
    git_objs = git.collect_objects(git_root)
    refs = git.collect_refs(git_root)
    graph = graphviz.to_graphviz(git_objs, refs, hide_content)
    util.compile_pdf(dot_file, pdf_file, graph)


def _mainloop(
    git_root: Path,
    dot_file: Path,
    pdf_file: Path,
    pdf_viewer: str,
    operating_system: util.OS,
    hide_content: bool,
) -> None:
    """Create and open a PDF file that is continually refreshed as changes
    occurr in the Git repo.
    """
    state_cache = git.state(git_root)
    _create_graph_pdf(dot_file, pdf_file, git_root, hide_content)
    util.view(pdf_file, pdf_viewer, operating_system.shell_setting)

    while True:
        time.sleep(1)
        state_out = git.state(git_root)
        if state_cache != state_out:
            state_cache = state_out
            _create_graph_pdf(dot_file, pdf_file, git_root, hide_content)
