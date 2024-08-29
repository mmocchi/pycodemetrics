from pycodemetrics.metrics.py.python_metrics import PythonCodeMetrics, compute_metrics


def test_compute_metrics():
    """
    compute_metrics関数のテスト。
    Pythonコードを入力として、正しいPythonCodeMetricsオブジェクトを返すことを確認する。
    """
    # Arrange: テスト用のPythonコードを準備
    code = """
import os
import sys

def foo():
    # Single comment
    pass
"""

    # Act: compute_metrics関数を実行
    result = compute_metrics(code)

    # Assert: 期待されるPythonCodeMetricsオブジェクトと結果を比較
    expected_metrics = PythonCodeMetrics(
        lines_of_code=7,
        logical_lines_of_code=4,
        source_lines_of_code=4,
        comments=1,
        single_comments=1,
        multi=0,
        blank=2,
        import_count=2,
        cyclomatic_complexity=1,
        maintainability_index=100.0,
        cognitive_complexity=0,
    )
    assert result == expected_metrics
