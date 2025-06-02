import pandas as pd
import pytest

from pycodemetrics.cli.exporter import export


def test_export(tmp_path):
    """export関数が新規ファイルを正常に作成できることを確認する。

    Arrange:
        テスト用のDataFrameを作成
        エクスポート先パスを準備

    Act:
        export関数を実行してファイルを作成

    Assert:
        初期状態でファイルが存在しないことを確認
        export実行後にファイルが作成されていることを確認
    """
    # Arrange: テスト用のDataFrameとエクスポート先パスを準備
    df = pd.DataFrame([{"a": 1, "b": 2}])
    export_path = tmp_path.joinpath("test.csv")

    # Assert: 初期状態でファイルが存在しないことを確認
    assert not export_path.exists()

    # Act: export関数を実行してファイルを作成
    export(df, export_path)

    # Assert: ファイルが作成されていることを確認
    assert export_path.exists()


def test_export_already_exist_error(tmp_path):
    """既存ファイルに上書き指定がない場合にFileExistsErrorが発生することを確認する。

    Arrange:
        テスト用のDataFrameを作成
        既存のエクスポートファイルを作成

    Act:
        上書き指定なしでexport関数を実行

    Assert:
        FileExistsErrorが発生することを確認
    """
    # Arrange: テスト用のDataFrameと既存ファイルを準備
    df = pd.DataFrame([{"a": 1, "b": 2}])
    export_path = tmp_path.joinpath("test.csv")
    export_path.touch()

    # Act & Assert: 上書き指定なしでexport関数を実行し、FileExistsErrorが発生することを確認
    with pytest.raises(FileExistsError):
        export(df, export_path)


def test_export_already_exist_overwrite(tmp_path):
    """既存ファイルに上書き指定がある場合に正常に上書きされることを確認する。

    Arrange:
        テスト用のDataFrameを作成
        既存のエクスポートファイルを作成

    Act:
        overwrite=Trueでexport関数を実行

    Assert:
        初期状態でファイルが存在することを確認
        export実行後にファイルが存在し続けることを確認
    """
    # Arrange: テスト用のDataFrameと既存ファイルを準備
    df = pd.DataFrame([{"a": 1, "b": 2}])
    export_path = tmp_path.joinpath("test.csv")
    export_path.touch()

    # Assert: 初期状態でファイルが存在することを確認
    assert export_path.exists()

    # Act: overwrite=Trueでexport関数を実行
    export(df, export_path, overwrite=True)

    # Assert: ファイルが存在し続けることを確認
    assert export_path.exists()
