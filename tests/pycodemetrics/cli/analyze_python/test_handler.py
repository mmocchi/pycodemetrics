from pathlib import Path

import pandas as pd

from pycodemetrics.cli.analyze_python.handler import (
    DisplayFormat,
    DisplayParameter,
    ExportParameter,
    InputTargetParameter,
    run_analyze_python_metrics,
)


def test_run_analyze_python_metrics(tmp_path, capsys):
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

    # Act
    # 解析を実行
    run_analyze_python_metrics(input_param, display_param, export_param)

    # 標準出力をキャプチャ
    captured = capsys.readouterr()

    # Assert

    # 期待される出力の検証
    assert "test_file.py" in captured.out
    assert "product" in captured.out  # プロダクトコードとして認識されることを確認

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
        assert metric in captured.out

    # 値の存在を確認（厳密な値は環境によって変わる可能性があるため、存在チェックのみ）
    assert any(char.isdigit() for char in captured.out)


def test_run_analyze_python_metrics_with_export(tmp_path):
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

    # Act
    # 解析を実行
    run_analyze_python_metrics(input_param, display_param, export_param)

    # Assert
    # エクスポートファイルの存在を確認
    assert export_file.exists()

    # エクスポートされたCSVの内容を確認
    df = pd.read_csv(export_file)
    assert "filepath" in df.columns
    assert "code_type" in df.columns
    assert len(df) == 1  # 1つのファイルのみ解析されたことを確認
    assert Path(df.iloc[0]["filepath"]).name == "test_file.py"
    assert df.iloc[0]["code_type"] == "product"
