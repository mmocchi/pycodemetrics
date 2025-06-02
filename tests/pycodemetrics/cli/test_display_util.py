import pandas as pd

from pycodemetrics.cli.display_util import DisplayFormat, display


def test_display_format_by_table(capsys):
    """TABLEフォーマットでデータが正常に表示されることを確認する。

    Arrange:
        テスト用のDataFrameを作成

    Act:
        TABLEフォーマットでdisplay関数を実行

    Assert:
        標準出力にテーブル形式のヘッダーが含まれていることを確認
        標準出力にテーブル形式のデータが含まれていることを確認
    """
    # Arrange: テスト用のDataFrameを作成
    df = pd.DataFrame([{"a": 1, "b": 2}])

    # Act: TABLEフォーマットでdisplay関数を実行
    display(df, DisplayFormat.TABLE)
    captured = capsys.readouterr()

    # Assert: テーブル形式の出力確認
    assert "a    b" in captured.out
    assert "1    2" in captured.out


def test_display_format_by_csv(capsys):
    """CSVフォーマットでデータが正常に表示されることを確認する。

    Arrange:
        テスト用のDataFrameを作成

    Act:
        CSVフォーマットでdisplay関数を実行

    Assert:
        標準出力にCSV形式のヘッダーが含まれていることを確認
        標準出力にCSV形式のデータが含まれていることを確認
    """
    # Arrange: テスト用のDataFrameを作成
    df = pd.DataFrame([{"a": 1, "b": 2}])

    # Act: CSVフォーマットでdisplay関数を実行
    display(df, DisplayFormat.CSV)
    captured = capsys.readouterr()

    # Assert: CSV形式の出力確認
    assert "a,b" in captured.out
    assert "1,2" in captured.out


def test_display_format_by_json(capsys):
    """JSONフォーマットでデータが正常に表示されることを確認する。

    Arrange:
        テスト用のDataFrameを作成

    Act:
        JSONフォーマットでdisplay関数を実行

    Assert:
        標準出力にJSON形式のデータが含まれていることを確認
    """
    # Arrange: テスト用のDataFrameを作成
    df = pd.DataFrame([{"a": 1, "b": 2}])

    # Act: JSONフォーマットでdisplay関数を実行
    display(df, DisplayFormat.JSON)
    captured = capsys.readouterr()

    # Assert: JSON形式の出力確認
    assert '[\n  {\n    "a":1,\n    "b":2\n  }\n]\n' in captured.out
