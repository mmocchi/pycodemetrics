"""analyze_coupling.pyのテストモジュール。"""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from pycodemetrics.metrics.coupling import CouplingMetrics, ProjectCouplingMetrics
from pycodemetrics.services.analyze_coupling import (
    CouplingAnalysisResult,
    CouplingAnalysisSettings,
    ModuleRecommendation,
    _create_empty_result,
    _generate_analysis_summary,
    _identify_problematic_modules,
    _identify_stable_modules,
    analyze_project_coupling_comprehensive,
    get_coupling_insights,
)


class TestCouplingAnalysisSettings:
    """CouplingAnalysisSettingsのテストクラス。"""

    def test_default_settings(self) -> None:
        """デフォルト設定のテスト。"""
        settings = CouplingAnalysisSettings()

        assert "__pycache__" in settings.exclude_patterns
        assert ".git" in settings.exclude_patterns
        assert settings.instability_threshold_high == 0.8
        assert settings.instability_threshold_low == 0.2
        assert settings.coupling_threshold_high == 5
        assert settings.lines_threshold_large == 200

    def test_custom_settings(self) -> None:
        """カスタム設定のテスト。"""
        settings = CouplingAnalysisSettings(
            exclude_patterns=["test"],
            instability_threshold_high=0.9,
            coupling_threshold_high=10,
        )

        assert settings.exclude_patterns == ["test"]
        assert settings.instability_threshold_high == 0.9
        assert settings.coupling_threshold_high == 10


class TestModuleRecommendation:
    """ModuleRecommendationのテストクラス。"""

    def test_module_recommendation_creation(self) -> None:
        """ModuleRecommendationの作成テスト。"""
        recommendation = ModuleRecommendation(
            module_path="test/module.py",
            priority="high",
            category="coupling",
            recommendations=["Fix coupling"],
            rationale="High coupling detected",
        )

        assert recommendation.module_path == "test/module.py"
        assert recommendation.priority == "high"
        assert recommendation.category == "coupling"
        assert recommendation.recommendations == ["Fix coupling"]
        assert recommendation.rationale == "High coupling detected"


class TestCouplingAnalysisResult:
    """CouplingAnalysisResultのテストクラス。"""

    def test_coupling_analysis_result_creation(self) -> None:
        """CouplingAnalysisResultの作成テスト。"""
        project_metrics = ProjectCouplingMetrics(
            project_path="/test",
            module_count=0,
            total_internal_dependencies=0,
            average_instability=0.0,
            max_afferent_coupling=0,
            max_efferent_coupling=0,
            module_metrics=[],
        )

        result = CouplingAnalysisResult(
            project_metrics=project_metrics,
            problematic_modules=[],
            stable_modules=[],
            recommendations=[],
            analysis_summary={},
        )

        assert result.project_metrics == project_metrics
        assert result.problematic_modules == []
        assert result.stable_modules == []
        assert result.recommendations == []
        assert result.analysis_summary == {}


class TestAnalyzeProjectCouplingComprehensive:
    """analyze_project_coupling_comprehensive関数のテストクラス。"""

    def test_invalid_project_path(self) -> None:
        """無効なプロジェクトパスでのテスト。"""
        with pytest.raises(ValueError, match="Invalid project path"):
            analyze_project_coupling_comprehensive(Path("/nonexistent/path"))

    @patch("pycodemetrics.services.analyze_coupling.analyze_project_coupling")
    def test_empty_project(self, mock_analyze: MagicMock) -> None:
        """空のプロジェクトでのテスト。"""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)

            mock_project_metrics = ProjectCouplingMetrics(
                project_path=str(project_path),
                module_count=0,
                total_internal_dependencies=0,
                average_instability=0.0,
                max_afferent_coupling=0,
                max_efferent_coupling=0,
                module_metrics=[],
            )
            mock_analyze.return_value = mock_project_metrics

            result = analyze_project_coupling_comprehensive(project_path)

            assert result.project_metrics.module_count == 0
            assert len(result.problematic_modules) == 0
            assert len(result.stable_modules) == 0
            assert len(result.recommendations) == 0

    @patch("pycodemetrics.services.analyze_coupling.analyze_project_coupling")
    def test_analysis_with_exception(self, mock_analyze: MagicMock) -> None:
        """分析中に例外が発生した場合のテスト。"""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)

            mock_analyze.side_effect = Exception("Analysis failed")

            with pytest.raises(RuntimeError, match="Coupling analysis failed"):
                analyze_project_coupling_comprehensive(project_path)


class TestCreateEmptyResult:
    """_create_empty_result関数のテストクラス。"""

    def test_create_empty_result(self) -> None:
        """空の結果作成のテスト。"""
        project_metrics = ProjectCouplingMetrics(
            project_path="/test",
            module_count=0,
            total_internal_dependencies=0,
            average_instability=0.0,
            max_afferent_coupling=0,
            max_efferent_coupling=0,
            module_metrics=[],
        )

        result = _create_empty_result(Path("/test"), project_metrics)

        assert result.project_metrics == project_metrics
        assert result.problematic_modules == []
        assert result.stable_modules == []
        assert result.recommendations == []
        assert result.analysis_summary["total_modules"] == 0
        assert result.analysis_summary["overall_health"] == "unknown"


class TestIdentifyProblematicModules:
    """_identify_problematic_modules関数のテストクラス。"""

    def test_identify_problematic_modules_high_instability(self) -> None:
        """高不安定度モジュールの特定テスト。"""
        settings = CouplingAnalysisSettings()
        modules = [
            CouplingMetrics(
                module_path="test.py",
                afferent_coupling=1,
                efferent_coupling=9,
                instability=0.9,
                lines_of_code=100,
            )
        ]

        problematic = _identify_problematic_modules(modules, settings)
        assert len(problematic) == 1
        assert problematic[0].module_path == "test.py"

    def test_identify_problematic_modules_high_coupling(self) -> None:
        """高結合度モジュールの特定テスト。"""
        settings = CouplingAnalysisSettings()
        modules = [
            CouplingMetrics(
                module_path="test.py",
                afferent_coupling=6,
                efferent_coupling=3,
                instability=0.33,
                lines_of_code=100,
            )
        ]

        problematic = _identify_problematic_modules(modules, settings)
        assert len(problematic) == 1
        assert problematic[0].module_path == "test.py"

    def test_identify_problematic_modules_large_file_with_coupling(self) -> None:
        """大規模ファイル + 高結合の特定テスト。"""
        settings = CouplingAnalysisSettings()
        modules = [
            CouplingMetrics(
                module_path="test.py",
                afferent_coupling=2,
                efferent_coupling=4,
                instability=0.67,
                lines_of_code=250,
            )
        ]

        problematic = _identify_problematic_modules(modules, settings)
        assert len(problematic) == 1
        assert problematic[0].module_path == "test.py"

    def test_identify_problematic_modules_high_distance(self) -> None:
        """メインシーケンスからの距離が大きいモジュールの特定テスト。"""
        settings = CouplingAnalysisSettings()
        modules = [
            CouplingMetrics(
                module_path="test.py",
                afferent_coupling=5,
                efferent_coupling=0,
                instability=0.0,
                lines_of_code=100,
                abstractness=0.4,  # distance = |0.4 + 0.0 - 1| = 0.6 > 0.5
            )
        ]

        problematic = _identify_problematic_modules(modules, settings)
        assert len(problematic) == 1
        assert problematic[0].module_path == "test.py"


class TestIdentifyStableModules:
    """_identify_stable_modules関数のテストクラス。"""

    def test_identify_stable_modules(self) -> None:
        """安定したモジュールの特定テスト。"""
        settings = CouplingAnalysisSettings()
        modules = [
            CouplingMetrics(
                module_path="stable.py",
                afferent_coupling=3,
                efferent_coupling=2,
                instability=0.1,  # < 0.2 threshold
                lines_of_code=100,
            ),
            CouplingMetrics(
                module_path="unstable.py",
                afferent_coupling=1,
                efferent_coupling=8,
                instability=0.89,
                lines_of_code=100,
            ),
        ]

        stable = _identify_stable_modules(modules, settings)
        assert len(stable) == 1
        assert stable[0].module_path == "stable.py"


class TestGenerateAnalysisSummary:
    """_generate_analysis_summary関数のテストクラス。"""

    def test_generate_analysis_summary_excellent_health(self) -> None:
        """優秀な健全性のサマリー生成テスト。"""
        project_metrics = ProjectCouplingMetrics(
            project_path="/test",
            module_count=1,
            total_internal_dependencies=3,
            average_instability=0.33,
            max_afferent_coupling=2,
            max_efferent_coupling=1,
            module_metrics=[
                CouplingMetrics(
                    module_path="test.py",
                    afferent_coupling=2,
                    efferent_coupling=1,
                    instability=0.33,
                    lines_of_code=100,
                )
            ],
        )

        summary = _generate_analysis_summary(project_metrics, [], [])

        assert summary["total_modules"] == 1
        assert summary["problematic_modules"] == 0
        assert summary["stable_modules"] == 0
        assert summary["overall_health"] == "excellent"
        assert summary["category_distribution"]["stable"] == 1

    def test_generate_analysis_summary_poor_health(self) -> None:
        """深刻な健全性のサマリー生成テスト。"""
        problematic_module = CouplingMetrics(
            module_path="bad.py",
            afferent_coupling=1,
            efferent_coupling=9,
            instability=0.9,
            lines_of_code=100,
        )

        project_metrics = ProjectCouplingMetrics(
            project_path="/test",
            module_count=1,
            total_internal_dependencies=10,
            average_instability=0.9,
            max_afferent_coupling=1,
            max_efferent_coupling=9,
            module_metrics=[problematic_module],
        )

        summary = _generate_analysis_summary(project_metrics, [problematic_module], [])

        assert summary["total_modules"] == 1
        assert summary["problematic_modules"] == 1
        assert summary["problematic_ratio"] == 1.0
        assert summary["overall_health"] == "poor"


class TestGetCouplingInsights:
    """get_coupling_insights関数のテストクラス。"""

    def test_get_coupling_insights_excellent(self) -> None:
        """優秀なプロジェクトのインサイトテスト。"""
        project_metrics = ProjectCouplingMetrics(
            project_path="/test",
            module_count=10,
            total_internal_dependencies=20,
            average_instability=0.3,
            max_afferent_coupling=3,
            max_efferent_coupling=2,
            module_metrics=[],
        )

        analysis_result = CouplingAnalysisResult(
            project_metrics=project_metrics,
            problematic_modules=[],
            stable_modules=[],
            recommendations=[],
            analysis_summary={
                "overall_health": "excellent",
                "problematic_ratio": 0.0,
                "stable_ratio": 0.4,
            },
        )

        insights = get_coupling_insights(analysis_result)

        assert any("非常に良好" in insight for insight in insights)
        assert any("安定したモジュール" in insight for insight in insights)

    def test_get_coupling_insights_poor(self) -> None:
        """問題のあるプロジェクトのインサイトテスト。"""
        project_metrics = ProjectCouplingMetrics(
            project_path="/test",
            module_count=10,
            total_internal_dependencies=100,
            average_instability=0.8,
            max_afferent_coupling=10,
            max_efferent_coupling=15,
            module_metrics=[],
        )

        high_priority_recommendation = ModuleRecommendation(
            module_path="bad.py",
            priority="high",
            category="coupling",
            recommendations=["Fix it"],
            rationale="High coupling",
        )

        analysis_result = CouplingAnalysisResult(
            project_metrics=project_metrics,
            problematic_modules=[],
            stable_modules=[],
            recommendations=[high_priority_recommendation],
            analysis_summary={
                "overall_health": "poor",
                "problematic_ratio": 0.3,
                "stable_ratio": 0.1,
            },
        )

        insights = get_coupling_insights(analysis_result)

        assert any("深刻な問題" in insight for insight in insights)
        assert any("問題のあるモジュール" in insight for insight in insights)
        assert any("依存関係密度が高すぎます" in insight for insight in insights)
        assert any("平均不安定度が高すぎます" in insight for insight in insights)
        assert any("高優先度の改善項目" in insight for insight in insights)
