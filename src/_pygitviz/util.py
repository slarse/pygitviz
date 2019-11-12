"""Standalone utility functions."""
import subprocess
import pathlib
import sys
import collections

ENCODING = sys.getdefaultencoding()

OS = collections.namedtuple("OS", "name open_pdf_cmd shell_setting".split())
Linux = OS(name="Linux", open_pdf_cmd="xdg-open", shell_setting=False)
MacOS = OS(name="macOS", open_pdf_cmd="open", shell_setting=False)
Windows = OS(name="Windows", open_pdf_cmd="start", shell_setting=True)


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


def compile_pdf(dot_file, pdf_file, graphviz):
    dot_file.write_text(graphviz)
    captured_run(*f"dot -Tpdf {str(dot_file)} -o {str(pdf_file)}".split())


def view(pdf_file: pathlib.Path, pdf_viewer: str, shell: bool) -> None:
    """Open a PDF file with the provided viewer program in a subprocess."""
    subprocess.Popen(
        f"{pdf_viewer} {str(pdf_file)}".split(),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=shell,
    )
