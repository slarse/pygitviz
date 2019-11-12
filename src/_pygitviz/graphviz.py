"""Functions for converting Git objects to a Graphviz representation."""
from itertools import groupby
from typing import List

from _pygitviz import git
from _pygitviz import gitobject
from _pygitviz.gitobject import Type

_COLOR = {
    Type.BLOB: "azure",
    Type.TREE: "darkolivegreen1",
    Type.COMMIT: "darkslategray1",
}
_SHAPES = {Type.BLOB: "egg", Type.TREE: "folder", Type.COMMIT: "rect"}
_ORDER = {Type.BLOB: 0, Type.TREE: 1, Type.COMMIT: 2}
EMPTY = r"digraph G {}"


def to_graphviz(git_objects: List[gitobject.GitObject], refs: List[git.Ref]) -> str:
    """Return a string with graphviz representing the provided Git objects and
    refs.
    """
    if not git_objects:
        return EMPTY

    groups = {
        key: list(group)
        for key, group in groupby(
            sorted(git_objects, key=lambda o: _ORDER[o.obj_type]),
            key=lambda o: o.obj_type,
        )
    }

    output = ""
    if Type.TREE in groups or Type.BLOB in groups:
        content_objs = groups.get(Type.TREE, []) + groups.get(Type.BLOB, [])
        output += _to_cluster(content_objs, "Content")
    if Type.COMMIT in groups:
        output += _to_cluster(groups[Type.COMMIT], "Commits")
    if refs:
        output += "\n".join([_ref_to_graphviz(ref) for ref in refs])

    return f"""digraph G {{
nodesep=.3;
ranksep=.5;
node [style=filled];
rankdir=LR;
{output}
}}"""


def _to_cluster(git_objects: List[gitobject.GitObject], label: str) -> str:
    """Return a string with a graphviz cluster of the provided git objects."""
    content = "\n".join([_gitobj_to_graphviz(obj) for obj in git_objects])
    return f"""subgraph cluster_{label} {{
label="{label}";
style="rounded";
bgcolor=beige;
{content}
}}
"""


def _gitobj_to_graphviz(git_object: gitobject.GitObject) -> str:
    return _to_graphviz_node(git_object) + "\n" + _to_graphviz_edges(git_object)


def _ref_to_graphviz(ref: git.Ref) -> str:
    return "\n".join([f'"{ref.name}" [shape=rect];', f'"{ref.name}" -> "{ref.value}";'])


def _to_graphviz_node(git_object: gitobject.GitObject) -> str:
    color = _COLOR[git_object.obj_type]
    shape = _SHAPES[git_object.obj_type]
    return (
        f'"{git_object.short_sha}" [label="{git_object.obj_type.value}\n{git_object.short_sha}"'
        f",fillcolor={color},shape={shape}];"
    )


def _to_graphviz_edges(git_object: gitobject.GitObject) -> str:
    output = ""
    if git_object.children:
        for child in git_object.children:
            output += f'"{git_object.short_sha}" -> "{child.short_sha}" [label="{child.name}"];\n'
    if git_object.parents:
        for parent in git_object.parents:
            output += f'"{parent.short_sha}" -> "{git_object.short_sha}" [dir=back];\n'
    return output.strip()
