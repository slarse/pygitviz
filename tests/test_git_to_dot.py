import collections
import pathlib
import shutil
import tempfile

import pytest

from _pygitviz import git_to_dot

_RepoTestCase = collections.namedtuple("_RepoTestCase", "repo_zip expected_dot_file")

def _to_repo_test_case(repo_zip: pathlib.Path) -> _RepoTestCase:
    expected_dot_file = repo_zip.parent / f"{repo_zip.stem}.dot"
    if not expected_dot_file.is_file():
        raise ValueError(f"missing dot file '{expected_dot_file}'")

    return _RepoTestCase(repo_zip, expected_dot_file)

def _get_repo_test_cases():
    _git_repo_zips = (pathlib.Path(__file__).parent / "resources" / "git_repos").glob("*.zip")

    return [_to_repo_test_case(repo_zip) for repo_zip in _git_repo_zips]


@pytest.mark.parametrize("repo_test_case", _get_repo_test_cases())
def test_git_to_dot_creates_expected_dotfile(repo_test_case, tmp_path):
    shutil.unpack_archive(str(repo_test_case.repo_zip), tmp_path)
    git_dir, *_ = tmp_path.rglob(".git")
    expected_graph = repo_test_case.expected_dot_file.read_text(encoding="utf8")

    actual_graph = git_to_dot.git_to_dot(git_dir)

    assert actual_graph.strip() == expected_graph.strip()
