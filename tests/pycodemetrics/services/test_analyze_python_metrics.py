from pathlib import Path

import pytest

from pycodemetrics.metrics.py.python_metrics import PythonCodeMetrics
from pycodemetrics.services.analyze_python_metrics import (
    CodeType,
    PythonFileMetrics,
    _is_tests_file,
    _open,
    analyze_python_file,
    get_product_or_test,
)


@pytest.fixture
def mock_open(mocker):
    return mocker.patch(
        "pycodemetrics.services.analyze_python_metrics._open",
        return_value="def foo(): pass",
    )


@pytest.fixture
def mock_compute_metrics(mocker):
    return_value = PythonCodeMetrics(
        lines_of_code=10,
        logical_lines_of_code=10,
        source_lines_of_code=10,
        comments=10,
        single_comments=10,
        multi=10,
        blank=10,
        import_count=10,
        cyclomatic_complexity=10,
        maintainability_index=10.0,
        cognitive_complexity=10,
    )
    return mocker.patch(
        "pycodemetrics.services.analyze_python_metrics.compute_metrics",
        return_value=return_value,
    )


def test_analyze_python_file(mock_open, mock_compute_metrics):
    # Arrange: テスト用のファイルパスを準備
    filepath = Path("src/example.py")

    # Act: analyze_python_file関数を実行
    result = analyze_python_file(filepath)

    # Assert: 期待されるPythonFileMetricsオブジェクトと結果を比較
    expected_metrics = PythonFileMetrics(
        filepath=filepath,
        product_or_test="product",
        metrics=mock_compute_metrics.return_value,
    )
    assert result == expected_metrics


def test_is_tests_file():
    """
    _is_tests_file関数のテスト。
    ファイルパスがテストファイルパターンに一致するかどうかを確認する。
    """
    # Arrange: テスト用のファイルパスを準備
    test_file_path = Path("project/tests/test_example.py")
    non_test_file_path = Path("project/src/example.py")

    # Act & Assert: _is_tests_file関数を実行し、結果を確認
    assert _is_tests_file(test_file_path) is True
    assert _is_tests_file(non_test_file_path) is False


def test_get_product_or_test():
    # Arrange: テスト用のファイルパスを準備
    test_file_path = Path("project/tests/test_example.py")
    non_test_file_path = Path("project/src/example.py")

    # Act & Assert: _is_tests_file関数を実行し、結果を確認
    assert get_product_or_test(test_file_path) == CodeType.TEST
    assert get_product_or_test(non_test_file_path) == CodeType.PRODUCT


def test_to_flat(mock_open, mock_compute_metrics):
    """
    to_flat関数のテスト。
    ファイルパスを入力として、正しいdictオブジェクトを返すことを確認する。
    """
    # Arrange: テスト用のファイルパスを準備
    filepath = Path("src/example.py")

    # Act: analyze_python_file関数を実行
    result = analyze_python_file(filepath).to_flat()

    # Assert: 期待されるPythonFileMetricsオブジェクトと結果を比較
    expected_metrics = {
        "filepath": filepath,
        "product_or_test": "product",
        "lines_of_code": 10,
        "logical_lines_of_code": 10,
        "source_lines_of_code": 10,
        "comments": 10,
        "single_comments": 10,
        "multi": 10,
        "blank": 10,
        "import_count": 10,
        "cyclomatic_complexity": 10,
        "maintainability_index": 10.0,
        "cognitive_complexity": 10,
    }
    assert result == expected_metrics


def test_open_存在しないパスを渡してFileNotFoundErrorが返ってくる():
    with pytest.raises(FileNotFoundError):
        _open(Path("__n/o/t_e/x/i/s/t_f/i/l/e_p/a/t/h__"))
