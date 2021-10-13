"""Utility functions for interacting with Git."""
import sys
import pathlib
import enum
import zlib
import itertools
import tempfile
import subprocess
from typing import List, Dict, Optional
from collections import namedtuple


from _pygitviz import util
from _pygitviz import gitobject
from _pygitviz.gitobject import Type

Ref = namedtuple("Ref", "name value".split())


class CatFileOption(enum.Enum):
    TYPE = "-t"
    PRETTY = "-p"


def collect_objects(git_root: pathlib.Path) -> List[gitobject.GitObject]:
    """Return all Git objects in the .git/objects directory, or an empty list
    if the directory does not exist.
    """
    if not (git_root / "objects").is_dir():
        return []

    loose_git_objects = _collect_loose_git_objects(git_root)
    packed_git_objects = _collect_packed_git_objects(git_root)

    return loose_git_objects + packed_git_objects


def _collect_loose_git_objects(git_root: pathlib.Path) -> List[gitobject.GitObject]:
    objects_root = git_root / "objects"

    object_dirs = (d for d in objects_root.iterdir() if len(d.name) == 2 and d.is_dir())
    object_shas = (d.name + file.name for d in object_dirs for file in d.iterdir())

    git_objects = {sha: _create_git_object(sha, git_root) for sha in object_shas}
    _link_related_git_objects(git_objects, git_root)

    return list(git_objects.values())


def _create_git_object(sha, git_root):
    obj_type = Type(cat_file(sha, git_root, CatFileOption.TYPE))
    return gitobject.GitObject(sha=sha, obj_type=obj_type)


def _link_related_git_objects(git_objects, git_root):
    for obj in git_objects.values():
        if obj.obj_type == Type.TREE:
            _add_children(obj, git_objects, git_root)
        elif obj.obj_type == Type.COMMIT:
            _add_parents_and_tree(obj, git_objects, git_root)


def _collect_packed_git_objects(git_root: pathlib.Path) -> List[gitobject.GitObject]:
    objects_root = git_root / "objects"

    pack_dir = objects_root / "pack"
    pack_files = list(pack_dir.glob("*.pack"))
    if not pack_files:
        return []

    with tempfile.TemporaryDirectory() as cache_dir:
        util.captured_run("git", "init", cwd=cache_dir)
        _unpack_pack_files_to(pack_files, cache_dir)
        git_objects = _collect_loose_git_objects(pathlib.Path(cache_dir) / ".git")

    return git_objects


def _unpack_pack_files_to(pack_files, target_dir):
    for pack_file in pack_files:
        proc = subprocess.Popen(
            ["git", "unpack-objects"], stdin=subprocess.PIPE, cwd=target_dir
        )
        proc.communicate(pack_file.read_bytes())


def collect_refs(git_root):
    """Return concrete refs and the HEAD symbolic ref. Return
    nothing if there are no concrete refs.
    """
    symb_file = git_root / "HEAD"
    ref_heads = git_root / "refs" / "heads"
    refs = []
    if ref_heads.exists():
        refs += [
            Ref(f.name, util.short_sha(f.read_text(encoding=util.ENCODING).strip()))
            for f in ref_heads.iterdir()
        ]

    if symb_file.exists() and refs:  # only add HEAD if there are concrete refs
        symb_contents = symb_file.read_text(encoding=util.ENCODING).split()
        symb_value = (
            symb_contents[-1].split("/")[-1]
            if len(symb_contents) > 1
            else util.short_sha(symb_contents[-1])
        )
        refs.append(Ref("HEAD", symb_value))

    return refs


def state(git_root):
    """Return a hash of the current state of the .git directory. Only considers
    fsck verbose output and refs.
    """
    if not git_root.is_dir():
        return 0
    rc, stdout, stderr = util.captured_run(*"git fsck --full -v".split(), cwd=git_root)
    refs = "".join([ref.name + ref.value for ref in collect_refs(git_root)])
    return hash(stdout + stderr + refs)


def _is_hex(s: str) -> bool:
    try:
        int(s, 16)
    except ValueError:
        return False
    return True


def cat_file(sha: str, git_root: pathlib.Path, opt: CatFileOption) -> str:
    """Run operations similar to `git cat-file` on a Git object."""
    rc, stdout, stderr = util.captured_run(
        *f"git cat-file {opt.value} {sha}".split(), cwd=git_root
    )
    if rc != 0:
        raise RuntimeError(stderr.strip())
    return stdout.strip()


def _add_parents_and_tree(commit, git_objects, git_root):
    """Add parent reference (i.e. to the parent commit) and tree reference (to
    the top-level tree) to a commit object.
    """
    content = cat_file(commit.sha, git_root, CatFileOption.PRETTY)
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


def _add_children(tree, git_objects, git_root):
    """Add children to a tree git object."""
    for line in cat_file(tree.sha, git_root, CatFileOption.PRETTY).split("\n"):
        *_, sha, name = line.strip().split()
        child = git_objects[sha]
        tree.add_child(name, child)
