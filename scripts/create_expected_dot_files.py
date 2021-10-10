"""Script that creates dot files from the repositories stored in
tests/resources with the current version of pygitviz.
"""
import pathlib
import tempfile
import shutil

from _pygitviz.git_to_dot import git_to_dot

TEST_GIT_REPOS_DIR = (
    pathlib.Path(__file__).parent.parent / "tests" / "resources" / "git_repos"
)


def main():
    compressed_repos = TEST_GIT_REPOS_DIR.glob("*.zip")

    for compressed in compressed_repos:
        with tempfile.TemporaryDirectory() as unpack_dir:
            shutil.unpack_archive(str(compressed), unpack_dir)

            git_root, *_ = pathlib.Path(unpack_dir).rglob(".git")
            graph = git_to_dot(git_root)

            dot_file = compressed.parent / f"{compressed.stem}.dot"
            dot_file.write_text(graph, encoding="utf8")

            print(f"Created dotfile:\n\tdotfile={dot_file.name}\n\tsource={compressed.name}")


main()
