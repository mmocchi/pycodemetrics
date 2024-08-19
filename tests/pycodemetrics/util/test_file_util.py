from pathlib import Path

import pytest

from pycodemetrics.util.file_util import (
    get_target_files_by_git_ls_files,
    get_target_files_by_path,
)


# Test for get_target_files_by_path using tmpdir
def test_get_target_files_by_path_directory(tmpdir):
    """
    get_target_files_by_path関数がディレクトリ内のPythonファイルのみを正しく返すことをテストします。
    """
    # Arrange
    tmpdir = Path(tmpdir)
    subdir = tmpdir.joinpath("subdir")
    subdir.mkdir()
    subdir.joinpath("test1.py").touch()
    subdir.joinpath("test2.py").touch()
    subdir.joinpath("test3.txt").touch()

    # Act
    result = get_target_files_by_path(tmpdir)

    # Assert
    expected_files = [
        subdir.joinpath("test1.py"),
        subdir.joinpath("test2.py"),
    ]
    assert sorted(result) == sorted(expected_files)


def test_get_target_files_by_path_file(tmpdir):
    """
    get_target_files_by_path関数が単一のPythonファイルを正しく返すことをテストします。
    """
    # Arrange
    tmpdir = Path(tmpdir)
    file = tmpdir.joinpath("test_file.py")
    file.touch()

    # Act
    result = get_target_files_by_path(file)

    # Assert
    assert result == [file]


def test_get_target_files_by_path_invalid(tmpdir):
    """
    get_target_files_by_path関数が存在しないパスを渡されたときにValueErrorを発生させることをテストします。
    """
    # Arrange
    tmpdir = Path(tmpdir)
    invalid_path = tmpdir.joinpath("invalid_path")

    # Act & Assert
    with pytest.raises(ValueError, match=f"Invalid path: {invalid_path.as_posix()}"):
        get_target_files_by_path(invalid_path)


# Test for get_target_files_by_git_ls_files
def test_get_target_files_by_git_ls_files(mocker):
    """
    get_target_files_by_git_ls_files関数がGitリポジトリ内のPythonファイルのみを正しく返すことをテストします。
    """
    # Arrange
    mocker.patch(
        "pycodemetrics.util.file_util.list_git_files",
        return_value=[
            Path("file1.py"),
            Path("file2.txt"),
            Path("file3.py"),
            Path("file4.py"),
        ],
    )

    # Act
    result = get_target_files_by_git_ls_files(Path("some/repo"))

    # Assert
    assert result == [Path("file1.py"), Path("file3.py"), Path("file4.py")]
