"""結合度分析サービスモジュール。

このモジュールは、プロジェクト全体のモジュール結合度分析を行うためのサービスレイヤーを提供します。
ビジネスロジックの中核となる機能を集約し、CLIレイヤーとメトリクス計算レイヤーを仲介します。

主な機能:
    - プロジェクト結合度分析の実行
    - 結果のフィルタリングと分類
    - メトリクスの統計情報計算
    - 推奨アクションの生成
    - エラーハンドリングとログ記録

処理パターン:
    1. プロジェクト検証とメタデータ収集
    2. 結合度メトリクスの計算
    3. 結果の分析と分類
    4. 推奨アクションの生成
    5. 統計情報の集計

制限事項:
    - 大規模プロジェクトでは処理時間がかかる場合があります
    - 動的インポートは検出できません
    - 抽象度の計算は現在未実装です
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import BaseModel

from pycodemetrics.metrics.coupling import (
    CouplingMetrics,
    ProjectCouplingMetrics,
    analyze_project_coupling,
)

logger = logging.getLogger(__name__)


class CouplingAnalysisSettings(BaseModel, frozen=True, extra="forbid"):
    """結合度分析の設定を表すクラス。

    Attributes:
        exclude_patterns (List[str]): 除外するパターンのリスト
        instability_threshold_high (float): 高不安定度の閾値
        instability_threshold_low (float): 低不安定度の閾値
        coupling_threshold_high (int): 高結合度の閾値
        lines_threshold_large (int): 大規模ファイルの閾値
    """

    exclude_patterns: List[str] = [
        "__pycache__",
        ".git",
        ".pytest_cache",
        "node_modules",
        ".venv",
        "venv",
        ".mypy_cache",
        ".tox",
        "build",
        "dist",
    ]
    instability_threshold_high: float = 0.8
    instability_threshold_low: float = 0.2
    coupling_threshold_high: int = 5
    lines_threshold_large: int = 200


class ModuleRecommendation(BaseModel, frozen=True, extra="forbid"):
    """モジュールに対する推奨アクションを表すクラス。

    Attributes:
        module_path (str): 対象モジュールのパス
        priority (str): 優先度（high, medium, low）
        category (str): 問題カテゴリ
        recommendations (List[str]): 推奨アクションのリスト
        rationale (str): 推奨理由
    """

    module_path: str
    priority: str  # high, medium, low
    category: str  # instability, coupling, size, dependency
    recommendations: List[str]
    rationale: str


class CouplingAnalysisResult(BaseModel, frozen=True, extra="forbid"):
    """結合度分析の完全な結果を表すクラス。

    Attributes:
        project_metrics (ProjectCouplingMetrics): プロジェクト全体のメトリクス
        problematic_modules (List[CouplingMetrics]): 問題のあるモジュール
        stable_modules (List[CouplingMetrics]): 安定したモジュール
        recommendations (List[ModuleRecommendation]): 推奨アクション
        analysis_summary (Dict[str, Any]): 分析サマリー
    """

    project_metrics: ProjectCouplingMetrics
    problematic_modules: List[CouplingMetrics]
    stable_modules: List[CouplingMetrics]
    recommendations: List[ModuleRecommendation]
    analysis_summary: Dict[str, Any]


def analyze_project_coupling_comprehensive(
    project_path: Path, settings: Optional[CouplingAnalysisSettings] = None
) -> CouplingAnalysisResult:
    """プロジェクトの包括的な結合度分析を実行

    Args:
        project_path (Path): 分析対象のプロジェクトパス
        settings (Optional[CouplingAnalysisSettings]): 分析設定

    Returns:
        CouplingAnalysisResult: 包括的な分析結果

    Raises:
        ValueError: プロジェクトパスが無効な場合
        RuntimeError: 分析処理でエラーが発生した場合
    """
    if settings is None:
        settings = CouplingAnalysisSettings()

    # プロジェクト検証
    if not project_path.exists() or not project_path.is_dir():
        raise ValueError(f"Invalid project path: {project_path}")

    logger.info(f"Starting comprehensive coupling analysis for: {project_path}")

    try:
        # 基本的な結合度分析
        project_metrics = analyze_project_coupling(
            project_path, settings.exclude_patterns
        )

        if project_metrics.module_count == 0:
            logger.warning("No Python modules found in the project")
            return _create_empty_result(project_path, project_metrics)

        # 問題のあるモジュールの特定
        problematic_modules = _identify_problematic_modules(
            project_metrics.module_metrics, settings
        )

        # 安定したモジュールの特定
        stable_modules = _identify_stable_modules(
            project_metrics.module_metrics, settings
        )

        # 推奨アクションの生成
        recommendations = _generate_recommendations(
            project_metrics.module_metrics, settings
        )

        # 分析サマリーの生成
        analysis_summary = _generate_analysis_summary(
            project_metrics, problematic_modules, stable_modules
        )

        logger.info(
            f"Analysis completed: {project_metrics.module_count} modules, "
            f"{len(problematic_modules)} problematic, {len(recommendations)} recommendations"
        )

        return CouplingAnalysisResult(
            project_metrics=project_metrics,
            problematic_modules=problematic_modules,
            stable_modules=stable_modules,
            recommendations=recommendations,
            analysis_summary=analysis_summary,
        )

    except Exception as e:
        logger.error(f"Failed to analyze project coupling: {e}")
        raise RuntimeError(f"Coupling analysis failed: {e}") from e


def _create_empty_result(
    project_path: Path, project_metrics: ProjectCouplingMetrics
) -> CouplingAnalysisResult:
    """空の分析結果を作成"""
    return CouplingAnalysisResult(
        project_metrics=project_metrics,
        problematic_modules=[],
        stable_modules=[],
        recommendations=[],
        analysis_summary={
            "total_modules": 0,
            "problematic_modules": 0,
            "stable_modules": 0,
            "recommendations": 0,
            "overall_health": "unknown",
        },
    )


def _identify_problematic_modules(
    modules: List[CouplingMetrics], settings: CouplingAnalysisSettings
) -> List[CouplingMetrics]:
    """問題のあるモジュールを特定"""
    problematic = []

    for module in modules:
        is_problematic = False

        # 高不安定度
        if module.instability > settings.instability_threshold_high:
            is_problematic = True

        # 高結合度
        if (
            module.afferent_coupling > settings.coupling_threshold_high
            or module.efferent_coupling > settings.coupling_threshold_high
        ):
            is_problematic = True

        # 大規模ファイル + 高結合
        if (
            module.lines_of_code > settings.lines_threshold_large
            and module.efferent_coupling > 3
        ):
            is_problematic = True

        # メインシーケンスからの距離が大きい
        if module.distance_from_main_sequence > 0.5:
            is_problematic = True

        if is_problematic:
            problematic.append(module)

    return problematic


def _identify_stable_modules(
    modules: List[CouplingMetrics], settings: CouplingAnalysisSettings
) -> List[CouplingMetrics]:
    """安定したモジュールを特定"""
    stable = []

    for module in modules:
        # 低不安定度 + 適度な入力結合度
        if (
            module.instability < settings.instability_threshold_low
            and module.afferent_coupling >= 2
            and module.efferent_coupling <= 3
        ):
            stable.append(module)

    return stable


def _generate_instability_recommendations(
    module: CouplingMetrics, settings: CouplingAnalysisSettings
) -> tuple[List[str], str, str, str]:
    """不安定度に基づく推奨事項を生成"""
    if module.efferent_coupling > settings.coupling_threshold_high:
        recommendations = [
            "依存関係の削減を検討してください",
            "Dependency Injection パターンの適用を検討してください",
            "モジュールの分割を検討してください",
        ]
        priority = "high"
        category = "coupling"
        rationale = f"出力結合度が高く（{module.efferent_coupling}）、不安定です"
    else:
        recommendations = [
            "より多くのモジュールからの利用を促進してください",
            "インターフェースの安定化を検討してください",
        ]
        priority = "medium"
        category = "instability"
        rationale = (
            f"不安定度が高い（{module.instability:.2f}）ですが、依存関係は適切です"
        )
    return recommendations, priority, category, rationale


def _generate_coupling_recommendations(
    module: CouplingMetrics, settings: CouplingAnalysisSettings
) -> tuple[List[str], str, str, str]:
    """結合度に基づく推奨事項を生成"""
    recommendations = [
        "責任の分離を検討してください",
        "Facade パターンの適用を検討してください",
        "依存関係の見直しを行ってください",
    ]
    priority = "high" if module.efferent_coupling > 8 else "medium"
    category = "coupling"
    rationale = f"出力結合度が高すぎます（{module.efferent_coupling}）"
    return recommendations, priority, category, rationale


def _generate_size_recommendations(
    module: CouplingMetrics, settings: CouplingAnalysisSettings
) -> tuple[List[str], str, str, str]:
    """ファイルサイズに基づく推奨事項を生成"""
    recommendations = [
        "ファイルサイズが大きすぎます。分割を検討してください",
        "Single Responsibility Principle の適用を検討してください",
    ]
    priority = "medium"
    category = "size"
    rationale = f"ファイルが大きく（{module.lines_of_code}行）、依存関係も多いです"
    return recommendations, priority, category, rationale


def _generate_distance_recommendations(
    module: CouplingMetrics, settings: CouplingAnalysisSettings
) -> tuple[List[str], str, str, str]:
    """メインシーケンスからの距離に基づく推奨事項を生成"""
    if module.category == "painful":
        recommendations = [
            "抽象度を下げるか、不安定度を上げることを検討してください",
            "具体的な実装への移行を検討してください",
        ]
        priority = "medium"
        category = "dependency"
        rationale = "メインシーケンスから離れすぎています（painful zone）"
    else:  # useless
        recommendations = [
            "モジュールの必要性を再検討してください",
            "他のモジュールとの統合を検討してください",
        ]
        priority = "low"
        category = "dependency"
        rationale = "メインシーケンスから離れすぎています（useless zone）"
    return recommendations, priority, category, rationale


def _generate_recommendations(
    modules: List[CouplingMetrics], settings: CouplingAnalysisSettings
) -> List[ModuleRecommendation]:
    """推奨アクションを生成"""
    recommendations = []

    for module in modules:
        module_recommendations: List[str] = []
        priority = "low"
        category = "general"
        rationale = ""

        # 不安定度に基づく推奨
        if module.instability > settings.instability_threshold_high:
            module_recommendations, priority, category, rationale = (
                _generate_instability_recommendations(module, settings)
            )
        # 高結合度に基づく推奨
        elif module.efferent_coupling > settings.coupling_threshold_high:
            module_recommendations, priority, category, rationale = (
                _generate_coupling_recommendations(module, settings)
            )
        # 大規模ファイルに基づく推奨
        elif (
            module.lines_of_code > settings.lines_threshold_large
            and module.efferent_coupling > 3
        ):
            module_recommendations, priority, category, rationale = (
                _generate_size_recommendations(module, settings)
            )
        # メインシーケンスからの距離に基づく推奨
        elif module.distance_from_main_sequence > 0.5 and module.category in [
            "painful",
            "useless",
        ]:
            module_recommendations, priority, category, rationale = (
                _generate_distance_recommendations(module, settings)
            )

        # 推奨事項がある場合のみ追加
        if module_recommendations:
            recommendations.append(
                ModuleRecommendation(
                    module_path=module.module_path,
                    priority=priority,
                    category=category,
                    recommendations=module_recommendations,
                    rationale=rationale,
                )
            )

    # 優先度でソート
    priority_order = {"high": 0, "medium": 1, "low": 2}
    recommendations.sort(key=lambda x: priority_order.get(x.priority, 3))

    return recommendations


def _generate_analysis_summary(
    project_metrics: ProjectCouplingMetrics,
    problematic_modules: List[CouplingMetrics],
    stable_modules: List[CouplingMetrics],
) -> Dict[str, Any]:
    """分析サマリーを生成"""
    total_modules = project_metrics.module_count
    problematic_count = len(problematic_modules)
    stable_count = len(stable_modules)

    # 全体的な健全性の評価
    if total_modules == 0:
        overall_health = "unknown"
    elif problematic_count / total_modules > 0.3:
        overall_health = "poor"
    elif problematic_count / total_modules > 0.1:
        overall_health = "fair"
    elif stable_count / total_modules > 0.2:
        overall_health = "good"
    else:
        overall_health = "excellent"

    # カテゴリ別の分布
    category_distribution: Dict[str, int] = {}
    for module in project_metrics.module_metrics:
        category = module.category
        category_distribution[category] = category_distribution.get(category, 0) + 1

    return {
        "total_modules": total_modules,
        "problematic_modules": problematic_count,
        "stable_modules": stable_count,
        "problematic_ratio": round(problematic_count / total_modules, 3)
        if total_modules > 0
        else 0,
        "stable_ratio": round(stable_count / total_modules, 3)
        if total_modules > 0
        else 0,
        "overall_health": overall_health,
        "average_instability": round(project_metrics.average_instability, 3),
        "dependency_density": round(project_metrics.dependency_density, 3),
        "category_distribution": category_distribution,
        "max_couplings": {
            "afferent": project_metrics.max_afferent_coupling,
            "efferent": project_metrics.max_efferent_coupling,
        },
    }


def get_coupling_insights(analysis_result: CouplingAnalysisResult) -> List[str]:
    """分析結果からインサイトを抽出

    Args:
        analysis_result (CouplingAnalysisResult): 分析結果

    Returns:
        List[str]: インサイトのリスト
    """
    insights = []
    summary = analysis_result.analysis_summary
    project_metrics = analysis_result.project_metrics

    # 全体的な評価
    health = summary["overall_health"]
    if health == "excellent":
        insights.append("🎉 プロジェクトの結合度は非常に良好です")
    elif health == "good":
        insights.append("✅ プロジェクトの結合度は良好です")
    elif health == "fair":
        insights.append("⚠️ プロジェクトの結合度に改善の余地があります")
    elif health == "poor":
        insights.append("🚨 プロジェクトの結合度に深刻な問題があります")

    # 具体的な問題の指摘
    if summary["problematic_ratio"] > 0.2:
        insights.append(
            f"問題のあるモジュールが {summary['problematic_ratio']:.1%} あります。リファクタリングを検討してください"
        )

    if project_metrics.dependency_density > 0.3:
        insights.append(
            f"依存関係密度が高すぎます（{project_metrics.dependency_density:.2f}）。モジュール間の結合を緩めることを検討してください"
        )

    if project_metrics.average_instability > 0.7:
        insights.append(
            f"平均不安定度が高すぎます（{project_metrics.average_instability:.2f}）。安定したインターフェースの設計を検討してください"
        )

    # ポジティブな指摘
    if summary["stable_ratio"] > 0.3:
        insights.append(
            f"安定したモジュールが {summary['stable_ratio']:.1%} あります。これらをコアライブラリとして活用できます"
        )

    # 推奨アクションのサマリー
    high_priority_count = len(
        [r for r in analysis_result.recommendations if r.priority == "high"]
    )
    if high_priority_count > 0:
        insights.append(f"高優先度の改善項目が {high_priority_count} 件あります")

    return insights
