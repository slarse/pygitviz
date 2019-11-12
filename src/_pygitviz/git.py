"""Utility functions for interacting with Git."""
import sys
import pathlib
from typing import List
from collections import namedtuple

from _pygitviz import util

Ref = namedtuple("Ref", "name value".split())

class GitObject:
    """Class representing an arbitrary Git object."""

    class _Child(namedtuple("_Child", "name obj".split())):
        def __getattr__(self, key):
            return self.__dict__.get(key, getattr(self.obj, key))

    def __init__(self, sha, type_, children=None, parents=None):
        self.sha = sha
        self.type_ = type_
        self._children = children or []
        self._parents = parents or []

    @property
    def short_sha(self):
        return short_sha(self.sha)

    @property
    def children(self):
        return list(self._children)

    @property
    def parents(self):
        return list(self._parents)

    def add_child(self, name, obj):
        self._children.append(self._Child(name, obj))

    def add_parent(self, obj):
        self._parents.append(obj)

    def __repr__(self):
        children_str = f", children={self.children}" if self.children else ""
        parent_str = f", parents={self.parents}" if self._parents else ""
        return f"{self.type_}(sha={self.short_sha}{parent_str}{children_str})"

    def __str__(self):
        return fr"{self.type_}\n{self.short_sha}"

    def __hash__(self):
        return int(self.sha, base=16)




def short_sha(sha: str) -> str:
    """Return an abbreviated version of the provided string."""
    return sha[:7]


def collect_objects(git_root: pathlib.Path) -> List[GitObject]:
    """Return all Git objects in the .git/objects directory, or an empty list
    if the directory does not exist.
    """
    objects_root = git_root / "objects"
    if not objects_root.is_dir():
        return []
    object_dirs = (d for d in objects_root.iterdir() if len(d.name) == 2 and d.is_dir())
    object_shas = (d.name + file.name for d in object_dirs for file in d.iterdir())
    git_objects = {
        sha: GitObject(sha=sha, type_=cat_file(sha, "-t"), children=set())
        for sha in object_shas
    }
    for obj in git_objects.values():
        if obj.type_ == "tree":
            _add_children(obj, git_objects)
        elif obj.type_ == "commit":
            _add_parents_and_tree(obj, git_objects)
    return git_objects.values()


def collect_refs(git_root):
    """Return concrete refs and the HEAD symbolic ref. Return
    nothing if there are no concrete refs.
    """
    symb_file = git_root / "HEAD"
    ref_heads = git_root / "refs" / "heads"
    refs = []
    if ref_heads.exists():
        refs += [
            Ref(f.name, short_sha(f.read_text(encoding=util.ENCODING).strip()))
            for f in ref_heads.iterdir()
        ]

    if symb_file.exists() and refs:  # only add HEAD if there are concrete refs
        symb_contents = symb_file.read_text(encoding=util.ENCODING).split()
        symb_value = (
            symb_contents[-1].split("/")[-1]
            if len(symb_contents) > 1
            else short_sha(symb_contents[-1])
        )
        refs.append(Ref("HEAD", symb_value))

    return refs


def state(git_root):
    """Return a hash of the current state of the .git directory. Only considers
    fsck verbose output and refs.
    """
    rc, stdout, stderr = util.captured_run(*"git fsck --full -v".split())
    refs = "".join([ref.name + ref.value for ref in collect_refs(git_root)])
    return hash(stdout + stderr + refs)


def cat_file(sha: str, *options) -> str:
    """Run `git cat-file` on a Git object."""
    options = " ".join(options)
    rc, stdout, stderr = util.captured_run(*f"git cat-file {options} {sha}".split())
    if rc != 0:
        raise RuntimeError(f"'git cat-file' exited with non-zero exit status for {sha}")
    return stdout.strip()


def _add_parents_and_tree(commit, git_objects):
    """Add parent reference (i.e. to the parent commit) and tree reference (to
    the top-level tree) to a commit object.
    """
    content = cat_file(commit.sha, "-p")
    ptr_str = content.split("\n")[0].strip()
    ptr_obj = git_objects[ptr_str.strip().split()[1]]
    commit.add_child("", ptr_obj)

    # parents may not exist
    for line in content.split("\n")[1:]:
        if line.startswith("author"):
            break
        elif line.startswith("parent"):
            _, parent_sha = line.strip().split()
            commit.add_parent(git_objects[parent_sha])


def _add_children(tree, git_objects):
    """Add children to a tree git object."""
    for line in cat_file(tree.sha, "-p").split("\n"):
        *_, sha, name = line.strip().split()
        child = git_objects[sha]
        tree.add_child(name, child)
