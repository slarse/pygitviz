"""Functions for converting Git objects to a Graphviz representation."""
from itertools import groupby
from typing import List

from _pygitviz import git
from _pygitviz import gitobject

_COLOR = {"blob": "azure", "tree": "darkolivegreen1", "commit": "darkslategray1"}
_SHAPES = {"blob": "egg", "tree": "folder", "commit": "rect"}
_ORDER = {"blob": 0, "tree": 1, "commit": 2}
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
            sorted(git_objects, key=lambda o: _ORDER[o.type_]), key=lambda o: o.type_
        )
    }

    output = ""
    if "tree" in groups or "blob" in groups:
        content_objs = groups.get("tree", []) + groups.get("blob", [])
        output += _to_cluster(content_objs, "Content")
    if "commit" in groups:
        output += _to_cluster(groups["commit"], "Commits")
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
    color = _COLOR[git_object.type_]
    shape = _SHAPES[git_object.type_]
    return (
        f'"{git_object.short_sha}" [label="{git_object.type_}\n{git_object.short_sha}"'
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
