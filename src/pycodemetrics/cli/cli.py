"""CLIモジュール。

このモジュールは、pycodemetricsのコマンドラインインターフェースを提供します。
各サブコマンドは、異なる分析機能を提供します。

主な機能:
    - コマンドライン引数の解析
    - サブコマンドの管理
    - ユーザー入力の検証

サブコマンド:
    - analyze_python_metrics: Pythonコードの分析
    - analyze_hotspot_metrics: コードのホットスポット分析
    - analyze_committer_metrics: コミッターの分析
    - test: テスト機能

制限事項:
    - このモジュールはCLIアプリケーションとしてのみ使用可能
    - 他のモジュールから直接インポートして使用することは想定していません
"""

import click

from pycodemetrics.cli.analyze_committer.cli import (
    committer as analyze_committer_metrics,
)
from pycodemetrics.cli.analyze_hotspot.cli import (
    hotspot as analyze_hotspot_metrics,
)
from pycodemetrics.cli.analyze_python.cli import (
    analyze as analyze_python_metrics,
)
from pycodemetrics.cli.sandbox import test


@click.group()
def cli() -> None:
    """PyCodeMetricsのメインコマンドグループ。

    このコマンドグループは、以下のサブコマンドを提供します：
    - analyze: Pythonコードの分析
    - hotspot: コードのホットスポット分析
    - committer: コミッターの分析
    - test: テスト機能

    Returns:
        None
    """


cli.add_command(analyze_python_metrics)
cli.add_command(analyze_hotspot_metrics)
cli.add_command(analyze_committer_metrics)
cli.add_command(test)


if __name__ == "__main__":
    cli()
