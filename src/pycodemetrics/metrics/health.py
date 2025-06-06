"""健康度メトリクス計算モジュール。

このモジュールは、プロジェクトの健康度を計算するためのメトリクス機能を提供します。
複数の指標を統合して総合的な健康度スコアを算出します。
"""

import logging
import statistics
from pathlib import Path
from typing import Any

from pydantic import BaseModel

logger = logging.getLogger(__name__)


class HealthMetrics(BaseModel, frozen=True, extra="forbid"):
    """健康度メトリクス。

    Args:
        overall_score: 総合健康度スコア (0-100)
        code_quality_score: コード品質スコア (0-100)
        architecture_score: アーキテクチャスコア (0-100)
        maintainability_score: 保守性スコア (0-100)
        evolution_score: 進化性スコア (0-100, オプション)
        critical_issues: 重要な問題のリスト
        recommendations: 推奨事項のリスト
        detailed_metrics: 詳細メトリクス
    """

    overall_score: int
    code_quality_score: int
    architecture_score: int
    maintainability_score: int
    evolution_score: int | None = None
    critical_issues: list[str] = []
    recommendations: list[str] = []
    detailed_metrics: dict[str, Any] = {}

    def to_dict(self) -> dict[str, Any]:
        return {
            "overall_score": self.overall_score,
            "code_quality_score": self.code_quality_score,
            "architecture_score": self.architecture_score,
            "maintainability_score": self.maintainability_score,
            "evolution_score": self.evolution_score,
            "critical_issues_count": len(self.critical_issues),
            "recommendations_count": len(self.recommendations),
            **self.detailed_metrics,
        }


class ProjectHealthResult(BaseModel, frozen=True, extra="forbid"):
    """プロジェクト健康度分析結果。"""

    target_path: Path
    health_metrics: HealthMetrics
    overall_score: int
    code_quality_score: int
    architecture_score: int
    maintainability_score: int
    evolution_score: int | None = None
    critical_issues: list[str] = []
    recommendations: list[str] = []

    def to_flat(self) -> dict[str, Any]:
        return {
            "target_path": str(self.target_path),
            **self.health_metrics.to_dict(),
        }


def analyze_project_health_metrics(
    python_metrics: list[Any],
    coupling_metrics: list[Any],
    hotspot_metrics: list[Any],
    include_trends: bool = False,
) -> HealthMetrics:
    """プロジェクトの健康度メトリクスを分析します。

    Args:
        python_metrics: Pythonメトリクスのリスト
        coupling_metrics: 結合度メトリクスのリスト
        hotspot_metrics: ホットスポットメトリクスのリスト
        include_trends: トレンド分析を含めるかどうか

    Returns:
        HealthMetrics: 健康度メトリクス
    """
    logger.info("Calculating health metrics...")

    # 各カテゴリのスコア計算
    code_quality_score = _calculate_code_quality_score(python_metrics)
    architecture_score = _calculate_architecture_score(coupling_metrics)
    maintainability_score = _calculate_maintainability_score(
        python_metrics, hotspot_metrics
    )

    evolution_score = None
    if include_trends:
        evolution_score = _calculate_evolution_score(hotspot_metrics)

    # 総合スコア計算
    scores = [code_quality_score, architecture_score, maintainability_score]
    if evolution_score is not None:
        scores.append(evolution_score)

    overall_score = round(statistics.mean(scores))

    # 問題と推奨事項の生成
    critical_issues = _generate_critical_issues(
        python_metrics, coupling_metrics, hotspot_metrics
    )
    recommendations = _generate_recommendations(
        code_quality_score, architecture_score, maintainability_score
    )

    # 詳細メトリクス
    detailed_metrics = _calculate_detailed_metrics(
        python_metrics, coupling_metrics, hotspot_metrics
    )

    return HealthMetrics(
        overall_score=overall_score,
        code_quality_score=code_quality_score,
        architecture_score=architecture_score,
        maintainability_score=maintainability_score,
        evolution_score=evolution_score,
        critical_issues=critical_issues,
        recommendations=recommendations,
        detailed_metrics=detailed_metrics,
    )


def _calculate_code_quality_score(python_metrics: list[Any]) -> int:
    """コード品質スコアを計算します。"""
    if not python_metrics:
        return 50  # デフォルトスコア

    try:
        # 複雑度の平均を計算
        complexities = []
        cognitive_complexities = []
        method_lengths = []

        for metric in python_metrics:
            if hasattr(metric, "metrics"):
                m = metric.metrics
                if hasattr(m, "cyclomatic_complexity"):
                    complexities.append(m.cyclomatic_complexity)
                if hasattr(m, "cognitive_complexity"):
                    cognitive_complexities.append(m.cognitive_complexity)
                if hasattr(m, "lines_of_code"):
                    method_lengths.append(m.lines_of_code)

        # スコア計算 (100点満点)
        complexity_score = _normalize_complexity_score(complexities)
        cognitive_score = _normalize_cognitive_score(cognitive_complexities)
        length_score = _normalize_length_score(method_lengths)

        # 重み付き平均
        quality_score = int(
            round(complexity_score * 0.4 + cognitive_score * 0.4 + length_score * 0.2)
        )

        return max(0, min(100, quality_score))

    except Exception as e:
        logger.warning(f"Error calculating code quality score: {e}")
        return 50


def _calculate_architecture_score(coupling_metrics: list[Any]) -> int:
    """アーキテクチャスコアを計算します。"""
    if not coupling_metrics:
        return 70  # デフォルトスコア

    try:
        instabilities = []
        for metric in coupling_metrics:
            if hasattr(metric, "instability"):
                instabilities.append(metric.instability)

        if not instabilities:
            return 70

        # 理想的な不安定性の分散を評価
        avg_instability = statistics.mean(instabilities)
        instability_variance = (
            statistics.variance(instabilities) if len(instabilities) > 1 else 0
        )

        # スコア計算 (理想的な分散に近いほど高スコア)
        score = 100 - min(instability_variance * 100, 50)  # 分散ペナルティ
        score -= abs(avg_instability - 0.5) * 100  # 中央値からの偏差ペナルティ

        return max(0, min(100, round(score)))

    except Exception as e:
        logger.warning(f"Error calculating architecture score: {e}")
        return 70


def _calculate_maintainability_score(
    python_metrics: list[Any], hotspot_metrics: list[Any]
) -> int:
    """保守性スコアを計算します。"""
    if not python_metrics and not hotspot_metrics:
        return 60  # デフォルトスコア

    try:
        # ホットスポットの集中度を評価
        hotspot_penalty = 0
        if hotspot_metrics:
            # 変更頻度の高いファイルの割合
            high_change_files = sum(
                1
                for metric in hotspot_metrics
                if hasattr(metric, "change_count") and metric.change_count > 10
            )
            total_files = len(hotspot_metrics)
            hotspot_ratio = high_change_files / total_files if total_files > 0 else 0
            hotspot_penalty = int(hotspot_ratio * 30)  # 最大30点減点

        # ファイルサイズの分散を評価
        size_penalty = 0
        if python_metrics:
            sizes = []
            for metric in python_metrics:
                if hasattr(metric, "metrics") and hasattr(
                    metric.metrics, "lines_of_code"
                ):
                    sizes.append(metric.metrics.lines_of_code)

            if sizes:
                large_files = sum(1 for size in sizes if size > 500)
                size_penalty = int((large_files / len(sizes)) * 20)  # 最大20点減点

        base_score = 100
        maintainability_score = base_score - hotspot_penalty - size_penalty

        return max(0, min(100, round(maintainability_score)))

    except Exception as e:
        logger.warning(f"Error calculating maintainability score: {e}")
        return 60


def _calculate_evolution_score(hotspot_metrics: list[Any]) -> int:
    """進化性スコアを計算します（トレンド分析）。"""
    # 実装は将来のトレンド分析機能で拡張
    return 75  # 暫定スコア


def _normalize_complexity_score(complexities: list[int]) -> int:
    """複雑度スコアを正規化します。"""
    if not complexities:
        return 70

    avg_complexity = statistics.mean(complexities)
    # 複雑度10を基準とした正規化
    score = max(0, 100 - (avg_complexity - 5) * 10)
    return int(min(100, score))


def _normalize_cognitive_score(cognitive_complexities: list[int]) -> int:
    """認知的複雑度スコアを正規化します。"""
    if not cognitive_complexities:
        return 70

    avg_cognitive = statistics.mean(cognitive_complexities)
    # 認知的複雑度15を基準とした正規化
    score = max(0, 100 - (avg_cognitive - 8) * 8)
    return int(min(100, score))


def _normalize_length_score(lengths: list[int]) -> int:
    """長さスコアを正規化します。"""
    if not lengths:
        return 80

    avg_length = statistics.mean(lengths)
    # 50行を基準とした正規化
    score = max(0, 100 - (avg_length - 30) * 2)
    return int(min(100, score))


def _generate_critical_issues(
    python_metrics: list[Any],
    coupling_metrics: list[Any],
    hotspot_metrics: list[Any],
) -> list[str]:
    """重要な問題を生成します。"""
    issues = []

    # 高複雑度ファイルの検出
    high_complexity_files = _detect_high_complexity_files(python_metrics)
    if high_complexity_files:
        count = len(high_complexity_files)
        issues.append(f"{count} files with high complexity (>15)")

    # 不安定なモジュールの検出
    unstable_modules = _detect_unstable_modules(coupling_metrics)
    if unstable_modules:
        count = len(unstable_modules)
        issues.append(f"{count} highly unstable modules (I>0.8)")

    # ホットスポットの検出
    hotspot_files = _detect_hotspot_files(hotspot_metrics)
    if hotspot_files:
        count = len(hotspot_files)
        issues.append(f"{count} files with high change frequency (>20 changes)")

    return issues[:5]  # 上位5つまで


def _detect_high_complexity_files(python_metrics: list[Any]) -> list[str]:
    """高複雑度ファイルを検出します。"""
    high_complexity_files = []
    for metric in python_metrics:
        try:
            if (
                hasattr(metric, "metrics")
                and hasattr(metric, "filepath")
                and hasattr(metric.metrics, "cyclomatic_complexity")
                and metric.metrics.cyclomatic_complexity > 15
            ):
                high_complexity_files.append(str(metric.filepath))
        except Exception:
            continue
    return high_complexity_files


def _detect_unstable_modules(coupling_metrics: list[Any]) -> list[str]:
    """不安定なモジュールを検出します。"""
    unstable_modules = []
    for metric in coupling_metrics:
        try:
            if hasattr(metric, "instability") and metric.instability > 0.8:
                if hasattr(metric, "module_name"):
                    unstable_modules.append(metric.module_name)
        except Exception:
            continue
    return unstable_modules


def _detect_hotspot_files(hotspot_metrics: list[Any]) -> list[str]:
    """ホットスポットファイルを検出します。"""
    hotspot_files = []
    for metric in hotspot_metrics:
        try:
            if hasattr(metric, "change_count") and metric.change_count > 20:
                if hasattr(metric, "filepath"):
                    hotspot_files.append(str(metric.filepath))
        except Exception:
            continue
    return hotspot_files


def _generate_recommendations(
    code_quality_score: int,
    architecture_score: int,
    maintainability_score: int,
) -> list[str]:
    """推奨事項を生成します。"""
    recommendations = []

    if code_quality_score < 60:
        recommendations.append(
            "Refactor high-complexity methods to improve code readability"
        )

    if architecture_score < 60:
        recommendations.append(
            "Review module dependencies and reduce coupling between components"
        )

    if maintainability_score < 60:
        recommendations.append(
            "Split large files and address hotspot areas with frequent changes"
        )

    # 一般的な推奨事項
    if not recommendations:
        if min(code_quality_score, architecture_score, maintainability_score) < 80:
            recommendations.append(
                "Consider implementing automated code quality checks in CI/CD pipeline"
            )

    return recommendations


def _calculate_detailed_metrics(
    python_metrics: list[Any],
    coupling_metrics: list[Any],
    hotspot_metrics: list[Any],
) -> dict[str, Any]:
    """詳細メトリクスを計算します。"""
    return {
        "total_python_files": len(python_metrics),
        "total_modules": len(coupling_metrics),
        "total_hotspot_files": len(hotspot_metrics),
        "analysis_timestamp": "2024-01-01T00:00:00Z",  # 実際の実装では現在時刻
    }
