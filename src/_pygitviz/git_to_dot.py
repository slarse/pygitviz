import pathlib

from _pygitviz import git
from _pygitviz import graphviz


def git_to_dot(git_dir: pathlib.Path, hide_content: bool = False) -> str:
    git_objs = git.collect_objects(git_dir)
    refs = git.collect_refs(git_dir)
    return graphviz.to_graphviz(git_objs, refs, hide_content)

