# PyGitViz
PyGitViz is a small program for visualizing the most important content of a Git
repository, primarily commits, trees, blobs and branches. The current state of
the project is a proof of concept that works, but is not particularly user
friendly. It uses [Graphviz](https://graphviz.org/) to create a PDF of the Git
repository layout, and then renders it with any PDF viewer that is available.

## Demo
* [Screencast of (even earlier version of) PyGitViz](https://www.youtube.com/watch?v=_rLuz9gzDVQ)

The screencast demonstrates some basics of Git objects and branches, and uses
the precursor to PyGitViz for visualization.

## How to use
Install the package as instructed in the [Install section](#install), and run
PyGitViz in a terminal at the root directory of a Git project (i.e. in the same
directory where you find the `.git` repository).

```bash
$ pygitviz -h
```
for the command line options. If the command cannot be found, you probably have
not added the `bin` directory in which the script was installed to your path.
You should still be able to run PyGitViz explicitly as a Python module.

```bash
$ python3 -m pygitviz -h
```

If you're in a bash-like shell, add an `&` at the end of the command to put it
in the background.

```bash
$ pygitviz &
```
> **Important:** PyGitViz cannot handle pack files (that are created e.g. when
> you have very many loose Git objects, or when you push). PyGitViz should
> be used only with small, fresh projects.

### Selecting the PDF viewer
By default, PyGitViz will use the `xdg-open` command on Linux-based OSes,
`start` on Windows, and `open` on macOS. If you want to specify some other PDF
viewer, pass it as an argument for the `-p` option.

> **Windows note:** I find it easiest to simply associate the `.pdf` file type
> with the desired viewer, and then run with the default `start` command.

## Requirements
PyGitViz requires the following to run.

* Python 3.6 or higher
* A PDF viewer
    - The viewer should ideally refresh automatically when a PDF is updated, as
      PyGitViz will render a new PDF for each change it detects in the
      repository.
    - For Linux, I highly recommend
      [Evince](https://wiki.gnome.org/Apps/Evince), which refreshes
      automatically.
    - For macOS, the PDF Preview application that ships with the OS is used by
      default, and it kind of works, but you need to refocus on the window by
      hovering over it with your mouse cursor for it to refresh. For a smoother
      experience, I recommend [Skim](https://skim-app.sourceforge.io/).
    - For Windows, I find
      [SumatraPDF](https://github.com/sumatrapdfreader/sumatrapdf) to work
      well.
* The `dot` command line tool (part of [Graphviz](https://graphviz.org/)).

## Install
First install the requirements listed above. Then install PyGitViz directly
from this repo. If you're on a Linux-distro, or macOS, the following should
work:

```bash
$ python3 -m pip install --user git+https://github.com/slarse/pygitviz.git
```

> **Windows note:** You may need to replace `python3` with `python`.

## License
PyGitViz is under the MIT license, please see the [LICENSE](LICENSE) file for
details.