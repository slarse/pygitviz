"""Functions for converting Git objects to a Graphviz representation."""
import pathlib
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
_SHAPES = {Type.BLOB: "egg", Type.TREE: "folder", Type.COMMIT: "rect", Type.TAG: "rect"}
_ORDER = {Type.BLOB: 0, Type.TREE: 1, Type.COMMIT: 2, Type.TAG: 3}
EMPTY = r"digraph G {}"


def git_to_dot(git_dir: pathlib.Path, hide_content: bool = False) -> str:
    """Produce a dot file from a Git directory.

    This function is guaranteed to produce consistent output. Calling this
    function multiple times on the same Git directory (without changing
    its state) always produces the same output.

    Args:
        git_dir: The .git directory.
        hide_content: If True, blobs and trees are not shown.

    Returns:
        A dot Digraph.
    """
    git_objs = git.collect_objects(git_dir)
    annotated_tags = [obj for obj in git_objs if obj.obj_type == Type.TAG]
    refs = git.collect_refs(git_dir, annotated_tags)
    return to_graphviz(git_objs, refs, hide_content)


def to_graphviz(
    git_objects: List[gitobject.GitObject],
    refs: List[git.Ref],
    hide_content: bool,
) -> str:
    """Return a string with graphviz representing the provided Git objects and
    refs.

    This function is guaranteed to produce consistent output. Calling this
    function multiple times on the same input always produces the same output.

    Args:
        git_objects: A list of GitObjects to turn into a Graphviz Digraph.
        refs: A list of Git refs.
        hide_content: If True, trees and blobs are not added to the Digraph.
    """
    if not git_objects:
        return EMPTY

    sha_sorted_git_objects = sorted(git_objects, key=lambda go: go.sha)
    groups = {
        key: list(group)
        for key, group in groupby(
            sorted(sha_sorted_git_objects, key=lambda o: _ORDER[o.obj_type]),
            key=lambda o: o.obj_type,
        )
    }

    output = ""
    if not hide_content and (Type.TREE in groups or Type.BLOB in groups):
        content_objs = groups.get(Type.TREE, []) + groups.get(Type.BLOB, [])
        output += _to_cluster(content_objs, "Content")
    if Type.COMMIT in groups:
        output += _to_cluster(
            groups[Type.COMMIT], "Commits", show_children=not hide_content
        )
    if refs:
        output += "\n".join([_ref_to_graphviz(ref) for ref in sorted(refs)])

    return f"""digraph G {{
nodesep=.3;
ranksep=.5;
node [style=filled];
rankdir=LR;
{output}
}}"""


def _to_cluster(
    git_objects: List[gitobject.GitObject],
    label: str,
    show_children: bool = True,
    show_parents: bool = True,
) -> str:
    """Return a string with a graphviz cluster of the provided git objects."""
    content = "\n".join(
        [_gitobj_to_graphviz(obj, show_children, show_parents) for obj in git_objects]
    )
    return f"""subgraph cluster_{label} {{
label="{label}";
style="rounded";
bgcolor=beige;
{content}
}}
"""


def _gitobj_to_graphviz(
    git_object: gitobject.GitObject, show_children: bool, show_parents: bool
) -> str:
    return (
        _to_graphviz_node(git_object)
        + "\n"
        + _to_graphviz_edges(git_object, show_children, show_parents)
    )


def _ref_to_graphviz(ref: git.Ref) -> str:
    ref_parts = [f'"{ref.name}" [shape=rect];', f'"{ref.name}" -> "{ref.value}";']

    if ref.remote_tracking_branch:
        ref_parts.append(
            f'"{ref.name}" -> "{ref.remote_tracking_branch}" '
            "[arrowhead=none,style=dashed];"
        )

    return "\n".join(ref_parts)


def _to_graphviz_node(git_object: gitobject.GitObject) -> str:
    color = _COLOR[git_object.obj_type]
    shape = _SHAPES[git_object.obj_type]
    return (
        f'"{git_object.short_sha}" [label="{git_object.obj_type.value}\n{git_object.short_sha}"'
        f",fillcolor={color},shape={shape}];"
    )


def _to_graphviz_edges(
    git_object: gitobject.GitObject, show_children: bool, show_parents: bool
) -> str:
    output = ""
    if git_object.children and show_children:
        for child in git_object.children:
            output += f'"{git_object.short_sha}" -> "{child.short_sha}" [label="{child.name}"];\n'
    if git_object.parents and show_parents:
        for parent in git_object.parents:
            output += f'"{parent.short_sha}" -> "{git_object.short_sha}" [dir=back];\n'
    return output.strip()
