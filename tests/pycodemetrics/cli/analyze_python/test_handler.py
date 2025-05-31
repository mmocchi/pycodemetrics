"""Pythonコード分析ハンドラーのテストモジュール。

このモジュールは、pycodemetrics.cli.analyze_python.handlerモジュールの機能をテストします。
Pythonコードのメトリクス分析機能と、結果の表示・エクスポート機能を検証します。
"""

from pathlib import Path

import pandas as pd
import pytest

from pycodemetrics.cli.analyze_python.handler import (
    DisplayFormat,
    DisplayParameter,
    ExportParameter,
    InputTargetParameter,
    RuntimeParameter,
    run_analyze_python_metrics,
)
from pycodemetrics.services.analyze_python_metrics import FilterCodeType


def test_run_analyze_python_metrics(
    tmp_path: Path, capsys: pytest.CaptureFixture
) -> None:
    """Pythonコードのメトリクス分析機能をテストします。

    Arrange:
        テスト用のPythonファイルを作成
        入力パラメータ、表示パラメータ、エクスポートパラメータを設定

    Act:
        メトリクス分析を実行
        標準出力をキャプチャ

    Assert:
        出力にファイル名が含まれていることを確認
        プロダクトコードとして認識されることを確認
        各メトリクスが出力に含まれていることを確認
        メトリクスの値が数値として出力されていることを確認
    """
    # Arrange
    # テスト用のPythonファイルを作成
    test_file = tmp_path / "test_file.py"
    test_file.write_text("""
def example_function():
    print("Hello, World!")

class ExampleClass:
    def __init__(self):
        self.value = 42

    def example_method(self):
        return self.value
""")

    input_param = InputTargetParameter(path=tmp_path, with_git_repo=False)
    display_param = DisplayParameter(format=DisplayFormat.TABLE)
    export_param = ExportParameter(export_file_path=None)
    runtime_param = RuntimeParameter(workers=1, filter_code_type=FilterCodeType.PRODUCT)

    # Act
    # 解析を実行
    run_analyze_python_metrics(input_param, runtime_param, display_param, export_param)

    # 標準出力をキャプチャ
    captured = capsys.readouterr()

    # Assert
    # 期待される出力の検証
    assert "test_file.py" in captured.out, "出力にファイル名が含まれていません"
    assert "product" in captured.out, "プロダクトコードとして認識されていません"

    # メトリクスの存在を確認
    metrics = [
        "lines_of_code",
        "logical_lines_of_code",
        "source_lines_of_code",
        "comments",
        "single_comments",
        "multi",
        "blank",
        "import_count",
        "cyclomatic_complexity",
        "maintainability_index",
        "cognitive_complexity",
    ]
    for metric in metrics:
        assert metric in captured.out, f"メトリクス '{metric}' が出力に含まれていません"

    # 値の存在を確認（厳密な値は環境によって変わる可能性があるため、存在チェックのみ）
    assert any(char.isdigit() for char in captured.out), (
        "メトリクスの値が数値として出力されていません"
    )


def test_run_analyze_python_metrics_with_export(tmp_path: Path) -> None:
    """Pythonコードのメトリクス分析とエクスポート機能をテストします。

    Arrange:
        テスト用のPythonファイルを作成
        入力パラメータ、表示パラメータ、エクスポートパラメータを設定
        エクスポートファイルのパスを設定

    Act:
        メトリクス分析を実行し、結果をCSVファイルにエクスポート

    Assert:
        エクスポートファイルが存在することを確認
        CSVファイルに必要なカラムが存在することを確認
        CSVファイルの行数が1であることを確認
        ファイル名が正しいことを確認
        コードタイプが'product'であることを確認
    """
    # Arrange
    # テスト用のPythonファイルを作成
    test_file = tmp_path / "test_file.py"
    test_file.write_text("""
def example_function():
    print("Hello, World!")
""")

    export_file = tmp_path / "output.csv"

    input_param = InputTargetParameter(path=tmp_path, with_git_repo=False)
    display_param = DisplayParameter(format=DisplayFormat.CSV)
    export_param = ExportParameter(export_file_path=export_file)
    runtime_param = RuntimeParameter(workers=1, filter_code_type=FilterCodeType.PRODUCT)

    # Act
    # 解析を実行
    run_analyze_python_metrics(input_param, runtime_param, display_param, export_param)

    # Assert
    # エクスポートファイルの存在を確認
    assert export_file.exists(), "エクスポートファイルが作成されていません"

    # エクスポートされたCSVの内容を確認
    df = pd.read_csv(export_file)
    assert "filepath" in df.columns, "CSVファイルに'filepath'カラムが存在しません"
    assert "code_type" in df.columns, "CSVファイルに'code_type'カラムが存在しません"
    assert len(df) == 1, "CSVファイルの行数が1ではありません"
    assert Path(df.iloc[0]["filepath"]).name == "test_file.py", (
        "ファイル名が正しくありません"
    )
    assert df.iloc[0]["code_type"] == "product", "コードタイプが'product'ではありません"
