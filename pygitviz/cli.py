import time
import tempfile
import argparse
import sys
import collections
from pathlib import Path

from pygitviz import pygitviz


OS = collections.namedtuple("OS", "name open_pdf_cmd shell_setting".split())
Linux = OS(name="Linux", open_pdf_cmd="xdg-open", shell_setting=False)
MacOS = OS(name="macOS", open_pdf_cmd="open", shell_setting=False)
Windows = OS(name="Windows", open_pdf_cmd="start", shell_setting=True)


def create_parser(operating_system: OS):
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


def get_os(platform: str) -> OS:
    """Return defaults for the current OS."""
    if platform.startswith("linux"):
        return Linux
    if platform.startswith("darwin"):
        return MacOS
    if platform.startswith("win"):
        return Windows
    raise ValueError(f"unidentified operating system {platform}")


def main():
    operating_system = get_os(sys.platform)
    parser = create_parser(operating_system)
    args = parser.parse_args(sys.argv[1:])

    pdf_name = "graph.pdf"
    dot_name = "graph.dot"
    git_root = Path(".git")
    with tempfile.TemporaryDirectory() as tmpdir:
        state_cache = pygitviz.git_state(git_root)
        dot_file = Path(str(tmpdir)) / dot_name
        pdf_file = Path(str(tmpdir)) / pdf_name
        pygitviz.create_graph_pdf(dot_file, pdf_file, git_root)
        pygitviz.view(pdf_file, args.pdf_viewer, operating_system.shell_setting)

        while True:
            time.sleep(1)
            state_out = pygitviz.git_state(git_root)
            if state_cache != state_out:
                state_cache = state_out
                pygitviz.create_graph_pdf(dot_file, pdf_file, git_root)


if __name__ == "__main__":
    main()
