"""CLIモジュール。

このモジュールは、PyCodeMetricsのコマンドラインインターフェースを提供します。

主な機能:
    - コマンドライン引数の解析
    - サブコマンドの管理
    - 結果の表示とエクスポート
    - エラーハンドリング

含まれるサブコマンド:
    - analyze_python: Pythonコードの分析
    - analyze_hotspot: ホットスポット分析
    - analyze_committer: コミッター分析
"""

from enum import IntEnum


class RETURN_CODE(IntEnum):
    """コマンドの終了コード。

    SUCCESS: 正常終了
    ERROR: エラーによる終了
    """

    SUCCESS = 0
    ERROR = 1
