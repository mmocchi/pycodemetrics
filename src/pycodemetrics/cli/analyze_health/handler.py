"""健康度分析ハンドラーモジュール。

このモジュールは、健康度分析のCLI処理を実行するためのハンドラー関数とパラメータクラスを提供します。
"""

import logging
from enum import Enum
from pathlib import Path
from typing import Any

from pydantic import BaseModel

from pycodemetrics.services.analyze_health import (
    HealthAnalysisSettings,
    analyze_project_health,
)

logger = logging.getLogger(__name__)


class DisplayFormat(str, Enum):
    """表示フォーマット。"""

    DASHBOARD = "dashboard"
    TABLE = "table"
    JSON = "json"
    CSV = "csv"

    @classmethod
    def to_list(cls) -> list[str]:
        return [e.value for e in cls]


class InputTargetParameter(BaseModel, frozen=True, extra="forbid"):
    """入力対象パラメータ。"""

    path: Path


class DisplayParameter(BaseModel, frozen=True, extra="forbid"):
    """表示パラメータ。"""

    format: DisplayFormat
    include_trends: bool = False


class ExportParameter(BaseModel, frozen=True, extra="forbid"):
    """エクスポートパラメータ。"""

    export_file_path: Path | None
    overwrite: bool


class RuntimeParameter(BaseModel, frozen=True, extra="forbid"):
    """ランタイムパラメータ。"""

    workers: int | None


def run_analyze_health(
    input_param: InputTargetParameter,
    runtime_param: RuntimeParameter,
    display_param: DisplayParameter,
    export_param: ExportParameter,
) -> None:
    """健康度分析を実行します。

    Args:
        input_param: 入力対象パラメータ
        runtime_param: ランタイムパラメータ
        display_param: 表示パラメータ
        export_param: エクスポートパラメータ
    """
    logger.info(f"Starting health analysis for: {input_param.path}")

    # 分析設定の準備
    settings = HealthAnalysisSettings(
        include_trends=display_param.include_trends,
        workers=runtime_param.workers,
    )

    # 健康度分析の実行
    health_result = analyze_project_health(input_param.path, settings)

    # 結果の表示
    _display_health_result(health_result, display_param)

    # エクスポート処理
    if export_param.export_file_path:
        # 暫定的にエクスポート機能は無効化
        logger.warning("Export functionality temporarily disabled for health command")


def _display_health_result(health_result: Any, display_param: DisplayParameter) -> None:
    """健康度分析結果を表示します。"""
    if display_param.format == DisplayFormat.DASHBOARD:
        _display_dashboard(health_result)
    elif display_param.format == DisplayFormat.TABLE:
        _display_table(health_result)
    elif display_param.format == DisplayFormat.JSON:
        _display_json(health_result)
    elif display_param.format == DisplayFormat.CSV:
        _display_csv(health_result)


def _display_dashboard(health_result: Any) -> None:
    """ダッシュボード形式で表示します。"""
    print("\nProject Health Dashboard")
    print("=" * 40)
    print()

    # 総合スコア
    overall_score = health_result.overall_score
    status_emoji = _get_status_emoji(overall_score)
    status_text = _get_status_text(overall_score)

    print(f"Overall Health Score: {overall_score}/100 {status_emoji} {status_text}")
    print()

    # カテゴリ別スコア
    print("┌─────────────────────┬───────┬────────────────────────┐")
    print("│ Category            │ Score │ Status                 │")
    print("├─────────────────────┼───────┼────────────────────────┤")

    categories = [
        ("Code Quality", health_result.code_quality_score),
        ("Architecture", health_result.architecture_score),
        ("Maintainability", health_result.maintainability_score),
    ]

    if health_result.evolution_score is not None:
        categories.append(("Evolution Trend", health_result.evolution_score))

    for category, score in categories:
        emoji = _get_status_emoji(score)
        status = _get_status_text(score)
        print(f"│ {category:<19} │ {score:>5} │ {emoji} {status:<19} │")

    print("└─────────────────────┴───────┴────────────────────────┘")
    print()

    # 重要な問題
    if health_result.critical_issues:
        print("🔥 Critical Issues (Fix First):")
        for issue in health_result.critical_issues[:5]:  # 上位5つ
            print(f"• {issue}")
        print()

    # 推奨事項
    if health_result.recommendations:
        print("📈 Recommendations:")
        for i, rec in enumerate(health_result.recommendations[:3], 1):  # 上位3つ
            print(f"{i}. {rec}")
        print()


def _display_table(health_result: Any) -> None:
    """テーブル形式で表示します。"""
    # 暫定的にJSONで表示
    _display_json(health_result)


def _display_json(health_result: Any) -> None:
    """JSON形式で表示します。"""
    import json

    print(json.dumps(health_result.to_flat(), indent=2, ensure_ascii=False))


def _display_csv(health_result: Any) -> None:
    """CSV形式で表示します。"""
    import csv
    import sys

    data = health_result.to_flat()
    writer = csv.DictWriter(sys.stdout, fieldnames=data.keys())
    writer.writeheader()
    writer.writerow(data)


def _get_status_emoji(score: int) -> str:
    """スコアに基づく絵文字を取得します。"""
    if score >= 80:
        return "✅"
    elif score >= 60:
        return "⚠️"
    else:
        return "❌"


def _get_status_text(score: int) -> str:
    """スコアに基づくステータステキストを取得します。"""
    if score >= 80:
        return "Good"
    elif score >= 60:
        return "Needs Attention"
    else:
        return "Poor"
