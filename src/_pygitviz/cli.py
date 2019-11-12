"""The command line interface for PyGitViz."""
import time
import tempfile
import argparse
import sys
from pathlib import Path

from _pygitviz import graphviz
from _pygitviz import util
from _pygitviz import git


def main() -> None:
    """Run the PyGitViz program."""
    operating_system = util.get_os()
    parser = _create_parser(operating_system)
    args = parser.parse_args(sys.argv[1:])

    pdf_name = "graph.pdf"
    dot_name = "graph.dot"
    git_root = Path(".git")
    with tempfile.TemporaryDirectory() as tmpdir:
        dot_file = Path(str(tmpdir)) / dot_name
        pdf_file = Path(str(tmpdir)) / pdf_name
        _mainloop(git_root, dot_file, pdf_file, args.pdf_viewer, operating_system)


def _create_parser(operating_system: util.OS) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="PyGitViz",
        description="Git repository visualizer for education and demonstration purposes",
    )
    parser.add_argument(
        "-p",
        "--pdf-viewer",
        help=(
            "Program to open the resulting PDF file with. Defaults to "
            f"'{operating_system.open_pdf_cmd}'."
        ),
        default=operating_system.open_pdf_cmd,
    )
    return parser


def _create_graph_pdf(dot_file: Path, pdf_file: Path, git_root: Path) -> None:
    git_objs = git.collect_objects(git_root)
    refs = git.collect_refs(git_root)
    graph = graphviz.to_graphviz(git_objs, refs)
    util.compile_pdf(dot_file, pdf_file, graph)


def _mainloop(
    git_root: Path,
    dot_file: Path,
    pdf_file: Path,
    pdf_viewer: str,
    operating_system: util.OS,
) -> None:
    """Create and open a PDF file that is continually refreshed as changes
    occurr in the Git repo.
    """
    state_cache = git.state(git_root)
    _create_graph_pdf(dot_file, pdf_file, git_root)
    util.view(pdf_file, pdf_viewer, operating_system.shell_setting)

    while True:
        time.sleep(1)
        state_out = git.state(git_root)
        if state_cache != state_out:
            state_cache = state_out
            _create_graph_pdf(dot_file, pdf_file, git_root)
