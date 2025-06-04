"""couplingコマンドのCLIモジュール。

このモジュールは、プロジェクト全体のモジュール結合度分析のためのコマンドラインインターフェースを提供します。

主な機能:
    - プロジェクトルートの指定と検証
    - 結合度分析の実行
    - 表示オプションの制御
    - 結果のエクスポート

使用例:
    pycodemetrics coupling /path/to/project
    pycodemetrics coupling . --format json --export coupling.json
    pycodemetrics coupling src --limit 20 --sort instability
    pycodemetrics coupling . --filter unstable --threshold 0.8
"""

from pathlib import Path

import click

from pycodemetrics.cli.analyze_coupling.handler import (
    DisplayParameter,
    ExportParameter,
    FilterParameter,
    InputParameter,
    run_analyze_coupling,
)
from pycodemetrics.cli.display_util import DisplayFormat


@click.command("coupling")
@click.argument("project_path", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--format",
    "format_",
    type=click.Choice([format_.value for format_ in DisplayFormat]),
    default=DisplayFormat.TABLE.value,
    help="出力フォーマット",
)
@click.option(
    "--export",
    type=click.Path(path_type=Path),
    help="結果をファイルにエクスポートするパス",
)
@click.option(
    "--export-overwrite",
    is_flag=True,
    help="エクスポートファイルの上書きを許可",
)
@click.option(
    "--columns",
    help="表示する列をカンマ区切りで指定（例: module_path,afferent_coupling,efferent_coupling,instability）",
)
@click.option(
    "--limit",
    type=int,
    default=0,
    help="表示する行数の制限（0で制限なし）",
)
@click.option(
    "--sort",
    type=click.Choice(
        [
            "module_path",
            "afferent_coupling",
            "efferent_coupling",
            "instability",
            "lines_of_code",
            "category",
        ]
    ),
    default="instability",
    help="ソート対象の列",
)
@click.option(
    "--sort-desc",
    is_flag=True,
    default=True,
    help="降順でソート",
)
@click.option(
    "--filter",
    "filter_type",
    type=click.Choice(["all", "stable", "unstable", "high-coupling"]),
    default="all",
    help="表示するモジュールのフィルター",
)
@click.option(
    "--instability-threshold",
    type=float,
    default=0.8,
    help="不安定モジュールの閾値（--filter unstable使用時）",
)
@click.option(
    "--coupling-threshold",
    type=int,
    default=5,
    help="高結合モジュールの閾値（--filter high-coupling使用時）",
)
@click.option(
    "--exclude",
    multiple=True,
    help="除外するパターン（複数指定可能）",
)
@click.option(
    "--summary",
    is_flag=True,
    help="プロジェクト全体のサマリーも表示",
)
def coupling(
    project_path: Path,
    format_: str,
    export: Path | None,
    export_overwrite: bool,
    columns: str | None,
    limit: int,
    sort: str,
    sort_desc: bool,
    filter_type: str,
    instability_threshold: float,
    coupling_threshold: int,
    exclude: tuple[str, ...],
    summary: bool,
) -> None:
    """プロジェクトのモジュール結合度を分析します。

    PROJECT_PATH: 分析対象のプロジェクトルートディレクトリ

    結合度メトリクスの解釈:
    - Ca (Afferent Coupling): このモジュールに依存するモジュール数（高いほど重要）
    - Ce (Efferent Coupling): このモジュールが依存するモジュール数（高いほど複雑）
    - I (Instability): Ce / (Ca + Ce) 不安定度（1に近いほど変更の影響を受けやすい）

    カテゴリ:
    - stable: 安定・具象（理想的なユーティリティ）
    - unstable: 不安定・抽象（理想的なインターフェース）
    - painful: 安定・抽象（変更困難）
    - useless: 不安定・具象（価値の低い）
    """
    # パラメータの構築
    input_param = InputParameter(
        project_path=project_path,
        exclude_patterns=list(exclude) if exclude else None,
    )

    display_param = DisplayParameter(
        format=DisplayFormat(format_),
        columns=columns.split(",") if columns else None,
        limit=limit if limit > 0 else None,
        sort_column=sort,
        sort_desc=sort_desc,
        show_summary=summary,
    )

    filter_param = FilterParameter(
        filter_type=filter_type,
        instability_threshold=instability_threshold,
        coupling_threshold=coupling_threshold,
    )

    export_param = ExportParameter(
        export_file_path=export,
        overwrite=export_overwrite,
    )

    # 結合度分析の実行
    run_analyze_coupling(input_param, display_param, filter_param, export_param)
