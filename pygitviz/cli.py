import time
import tempfile
import argparse
import sys
from pathlib import Path

from pygitviz import pygitviz


def create_parser():
    default_open_command = os_default_open(sys.platform)
    parser = argparse.ArgumentParser(
        prog="PyGitViz",
        description="Git repository visualizer for education and demonstration purposes",
    )
    parser.add_argument(
        "-p",
        "--pdf-viewer",
        help=(
            "Program to open the resulting PDF file with. Defaults to "
            f"'{default_open_command}'."
        ),
        default=default_open_command,
    )
    return parser


def os_default_open(platform):
    """Identify the OS and return the default command to open files with."""
    if platform.startswith("linux"):
        open_command = "xdg-open"
    elif platform.startswith("darwin"):
        open_command = "open"
    elif platform.startswith("win"):
        open_command = "start"
    else:
        raise ValueError(
            "unidentified operating system, please specify PDF viewer explicitly"
        )
    return open_command


def main():
    parser = create_parser()
    args = parser.parse_args(sys.argv[1:])

    pdf_name = "graph.pdf"
    dot_name = "graph.dot"
    git_root = Path(".git")
    with tempfile.TemporaryDirectory() as tmpdir:
        state_cache = pygitviz.git_state(git_root)
        dot_file = Path(str(tmpdir)) / dot_name
        pdf_file = Path(str(tmpdir)) / pdf_name
        pygitviz.create_graph_pdf(dot_file, pdf_file, git_root)
        pygitviz.view(pdf_file, args.pdf_viewer)

        while True:
            time.sleep(1)
            state_out = pygitviz.git_state(git_root)
            if state_cache != state_out:
                state_cache = state_out
                pygitviz.create_graph_pdf(dot_file, pdf_file, git_root)


if __name__ == "__main__":
    main()
