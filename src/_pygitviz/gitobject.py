"""A class that represents a Git object."""
from collections import namedtuple
from typing import List

from _pygitviz import util


class Child(namedtuple("_Child", "name obj".split())):
    """A wrapper class for a GitObject that associates it with a name."""

    def __getattr__(self, key):
        return self.__dict__.get(key, getattr(self.obj, key))


class GitObject:
    """Class representing Git object."""

    def __init__(self, sha: str, type_: str):
        """
        Args:
            sha: The sha1 hexstring of this GitObject.
            type_: The type of this GitObject.
        """

        self.sha = sha
        self.type_ = type_
        self._children = []
        self._parents = []

    @property
    def short_sha(self) -> str:
        """Return an abbreviated form of this GitObject's sha1 hexstring."""
        return util.short_sha(self.sha)

    @property
    def children(self) -> List[Child]:
        """Return a copy of this GitObject's children."""
        return list(self._children)

    @property
    def parents(self) -> List["GitObject"]:
        """Return a copy of this GitObject's parents."""
        return list(self._parents)

    def add_child(self, name: str, obj: "GitObject") -> None:
        """Add the provided GitObject with the given name as a child to this
        GitObject.
        """
        self._children.append(Child(name, obj))

    def add_parent(self, obj: "GitObject") -> None:
        """Add a parent to this GitObject."""
        self._parents.append(obj)

    def __repr__(self) -> str:
        children_str = f", children={self.children}" if self.children else ""
        parent_str = f", parents={self.parents}" if self._parents else ""
        return f"{self.type_}(sha={self.short_sha}{parent_str}{children_str})"

    def __str__(self) -> str:
        return fr"{self.type_}\n{self.short_sha}"

    def __hash__(self) -> int:
        return int(self.sha, base=16)
