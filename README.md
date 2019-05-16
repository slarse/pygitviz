# PyGitViz
PyGitViz is a small program for visualizing the most important content of a Git
repository, primarily commits, trees, blobs and branches. The current state of
the project is a proof of concept that works, but is not particularly user
friendly.

## Demo
* [Screencast of (even earlier version of) PyGitViz](https://www.youtube.com/watch?v=_rLuz9gzDVQ)

The screencast demonstrates some basics of Git objects and branches, and uses
the precursor to PyGitViz for visualization.

## How to use
Install the package as instructed in the [Install section](#install), and run
PyGitViz in the root directory of a Git project (i.e. in the same directory
where you find the `.git` repositor).

```bash
$ pygitviz -h
```
for the command line options. If the command cannot be found, you probably have
not added the `bin` directory in which the script was installed to your path.
You should still be able to run PyGitViz explicitly as a Python module.

```bash
$ python3 -m pygitviz.cli
```

> **Important:** PyGitViz cannot handle pack files (that are created e.g. when
> you have very many loose Git objects, or when you push). PyGitViz should
> be used only with small, fresh projects.

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
* The `dot` command line tool (part of [Graphviz](https://graphviz.org/)).

## Install
First install the requirements listed above. Then install PyGitViz directly
from this repo.

```bash
$ python3 -m pip install --user git+https://github.com/slarse/pygitviz.git
```

## License
PyGitViz is under the MIT license, please see the [LICENSE](LICENSE) file for
details.
