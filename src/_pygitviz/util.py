"""Standalone utility functions."""
import subprocess
import pathlib
import sys
import collections
import enum

ENCODING = sys.getdefaultencoding()

OS = collections.namedtuple("OS", "name open_pdf_cmd shell_setting".split())
Linux = OS(name="Linux", open_pdf_cmd="xdg-open", shell_setting=False)
MacOS = OS(name="macOS", open_pdf_cmd="open", shell_setting=False)
Windows = OS(name="Windows", open_pdf_cmd="start", shell_setting=True)


class FileType(enum.Enum):
    PDF = "pdf"
    PNG = "png"


def short_sha(sha: str) -> str:
    """Return an abbreviated version of the provided SHA1 hexstring."""
    return sha[:7]


def get_os(platform: str = sys.platform) -> OS:
    """Return defaults for the current OS."""
    if platform.startswith("linux"):
        return Linux
    if platform.startswith("darwin"):
        return MacOS
    if platform.startswith("win"):
        return Windows
    raise ValueError(f"unidentified operating system {platform}")


def captured_run(*args, **kwargs):
    """Run a subprocess and capture the output."""
    proc = subprocess.run(
        args, **kwargs, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    return (proc.returncode, proc.stdout.decode(ENCODING), proc.stderr.decode(ENCODING))


def check_filetype_supported(path: pathlib.Path) -> None:
    """Check if the path points to a filetype that is supported as an output
    forat.
    """
    file_ext = path.suffix.lstrip(".")
    filetypes = [t.value for t in FileType]
    if file_ext not in filetypes:
        raise ValueError(
            f"unsupported filetype on '{path}'. "
            f"Supported filetypes: {', '.join(filetypes)}"
        )


def compile(
    dot_file: pathlib.Path,
    output_file: pathlib.Path,
    graph: str,
) -> None:
    dot_file.write_text(graph)
    output_format = FileType(output_file.suffix.lstrip("."))
    captured_run(*f"dot -T{output_format.value} {dot_file} -o {output_file}".split())


def compile_pdf(dot_file, pdf_file, graphviz):
    dot_file.write_text(graphviz)
    captured_run(*f"dot -Tpdf {dot_file} -o {pdf_file}".split())


def view(pdf_file: pathlib.Path, pdf_viewer: str, shell: bool) -> None:
    """Open a PDF file with the provided viewer program in a subprocess."""
    subprocess.Popen(
        f"{pdf_viewer} {pdf_file}".split(),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=shell,
    )
