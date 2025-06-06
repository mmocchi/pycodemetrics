"""プロジェクト健康度分析CLIモジュール。

このモジュールは、プロジェクト全体の健康度を分析するCLIコマンドを提供します。
複数のメトリクスを統合して、プロジェクトの総合的な健康状態を評価します。

主な機能:
    - コード品質の健康度分析
    - アーキテクチャの健康度分析
    - 保守性の健康度分析
    - 進化性の健康度分析
    - 総合健康度スコアの算出
    - 改善提案の表示

分析対象:
    - プロジェクト全体のPythonファイル
    - Gitリポジトリの変更履歴
    - モジュール間の結合関係

出力形式:
    - ダッシュボード形式（デフォルト）
    - JSON形式
    - CSV形式

制限事項:
    - 入力パスは存在する必要があります
    - Gitリポジトリが必要です（一部機能）
"""

import sys
from pathlib import Path

import click

from pycodemetrics.cli import RETURN_CODE
from pycodemetrics.cli.analyze_health.handler import (
    DisplayFormat,
    DisplayParameter,
    ExportParameter,
    InputTargetParameter,
    RuntimeParameter,
    run_analyze_health,
)


@click.command()
@click.argument("input_path", type=click.Path(exists=True))
@click.option(
    "--format",
    type=click.Choice(DisplayFormat.to_list(), case_sensitive=True),
    default=DisplayFormat.DASHBOARD.value,
    help=f"Output format, default: {DisplayFormat.DASHBOARD.value}",
)
@click.option(
    "--export",
    type=click.Path(file_okay=True, dir_okay=False),
    default=None,
    help="Export the result to the specified file path. If not specified, do not export.",
)
@click.option(
    "--export-overwrite",
    is_flag=True,
    default=False,
    help="Overwrite the export file if it already exists.",
)
@click.option(
    "--workers",
    type=click.IntRange(min=1),
    default=None,
    help="Number of workers for multiprocessing. If not specified, use the number of CPUs.",
)
@click.option(
    "--include-trends",
    is_flag=True,
    default=False,
    help="Include trend analysis (requires git repository).",
)
def health(
    input_path: str,
    format: str,
    export: str,
    export_overwrite: bool,
    workers: int | None,
    include_trends: bool,
) -> None:
    """Analyze project health metrics for the specified path

    INPUT_PATH: Path to the target directory or git repository directory.
    """

    try:
        # パラメータの設定
        input_param = InputTargetParameter(path=Path(input_path))

        display_param = DisplayParameter(
            format=DisplayFormat(format),
            include_trends=include_trends,
        )

        export_file_path = Path(export) if export else None
        export_param = ExportParameter(
            export_file_path=export_file_path, overwrite=export_overwrite
        )

        runtime_param = RuntimeParameter(workers=workers)

        # メイン処理の実行
        run_analyze_health(input_param, runtime_param, display_param, export_param)
        sys.exit(RETURN_CODE.SUCCESS)
    except Exception as e:
        click.echo(f"Error in health command: {type(e).__name__}: {str(e)}", err=True)
        raise e
