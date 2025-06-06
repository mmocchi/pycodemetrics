"""健康度分析ハンドラーのテストモジュール。"""

from pathlib import Path
from unittest.mock import Mock, patch

from pycodemetrics.cli.analyze_health.handler import (
    DisplayFormat,
    DisplayParameter,
    ExportParameter,
    InputTargetParameter,
    RuntimeParameter,
    _get_status_emoji,
    _get_status_text,
    run_analyze_health,
)


class TestDisplayFormat:
    """DisplayFormatクラスのテスト。"""

    def test_to_list(self):
        """to_list メソッドのテスト。"""
        expected = ["dashboard", "table", "json", "csv"]
        assert DisplayFormat.to_list() == expected


class TestStatusFunctions:
    """ステータス関数のテスト。"""

    def test_get_status_emoji(self):
        """_get_status_emoji 関数のテスト。"""
        assert _get_status_emoji(90) == "✅"
        assert _get_status_emoji(70) == "⚠️"
        assert _get_status_emoji(50) == "❌"

    def test_get_status_text(self):
        """_get_status_text 関数のテスト。"""
        assert _get_status_text(90) == "Good"
        assert _get_status_text(70) == "Needs Attention"
        assert _get_status_text(50) == "Poor"


class TestRunAnalyzeHealth:
    """run_analyze_health 関数のテスト。"""

    @patch("pycodemetrics.cli.analyze_health.handler.analyze_project_health")
    def test_basic_execution(self, mock_analyze):
        """基本的な実行のテスト。"""
        # モックの設定
        mock_result = Mock()
        mock_result.to_flat.return_value = {"score": 75}
        mock_result.overall_score = 75
        mock_result.code_quality_score = 70
        mock_result.architecture_score = 80
        mock_result.maintainability_score = 75
        mock_result.evolution_score = None
        mock_result.critical_issues = []
        mock_result.recommendations = []
        mock_analyze.return_value = mock_result

        # パラメータの設定
        input_param = InputTargetParameter(path=Path("/tmp"))
        runtime_param = RuntimeParameter(workers=1)
        display_param = DisplayParameter(format=DisplayFormat.DASHBOARD)
        export_param = ExportParameter(export_file_path=None, overwrite=False)

        # テスト実行（例外が発生しないことを確認）
        run_analyze_health(input_param, runtime_param, display_param, export_param)

        # analyze_project_health が呼び出されたことを確認
        mock_analyze.assert_called_once()


class TestParameterClasses:
    """パラメータクラスのテスト。"""

    def test_input_target_parameter(self):
        """InputTargetParameter のテスト。"""
        param = InputTargetParameter(path=Path("/tmp"))
        assert param.path == Path("/tmp")

    def test_display_parameter(self):
        """DisplayParameter のテスト。"""
        param = DisplayParameter(format=DisplayFormat.JSON, include_trends=True)
        assert param.format == DisplayFormat.JSON
        assert param.include_trends is True

    def test_export_parameter(self):
        """ExportParameter のテスト。"""
        param = ExportParameter(
            export_file_path=Path("/tmp/output.json"), overwrite=True
        )
        assert param.export_file_path == Path("/tmp/output.json")
        assert param.overwrite is True

    def test_runtime_parameter(self):
        """RuntimeParameter のテスト。"""
        param = RuntimeParameter(workers=4)
        assert param.workers == 4
