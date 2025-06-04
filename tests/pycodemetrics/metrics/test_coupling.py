"""couplingモジュールのテスト。

このテストモジュールは、モジュール結合度分析機能の正常性を検証します。

テスト対象:
    - ModuleDependency データモデル
    - CouplingMetrics データモデル
    - ProjectCouplingMetrics データモデル
    - EnhancedImportAnalyzer クラス
    - CouplingAnalyzer クラス
    - analyze_project_coupling 関数

テストケース:
    - 基本的な依存関係の検出
    - 結合度メトリクスの計算精度
    - プロジェクト全体の分析
    - エラーハンドリング
    - フィルタリングとカテゴリ分類
"""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from pycodemetrics.metrics.coupling import (
    CouplingAnalyzer,
    CouplingMetrics,
    EnhancedImportAnalyzer,
    ModuleDependency,
    ProjectCouplingMetrics,
    analyze_project_coupling,
)


class TestModuleDependency(unittest.TestCase):
    """ModuleDependencyクラスのテスト。"""

    def test_create_module_dependency(self):
        """ModuleDependencyの作成テスト。"""
        dependency = ModuleDependency(
            module_path="test/module.py",
            imported_modules=["os", "sys", "my_module"],
            internal_imports=["my_module"],
            external_imports=["os", "sys"],
            lines_of_code=100,
        )

        self.assertEqual(dependency.module_path, "test/module.py")
        self.assertEqual(len(dependency.imported_modules), 3)
        self.assertEqual(len(dependency.internal_imports), 1)
        self.assertEqual(len(dependency.external_imports), 2)
        self.assertEqual(dependency.lines_of_code, 100)


class TestCouplingMetrics(unittest.TestCase):
    """CouplingMetricsクラスのテスト。"""

    def test_create_coupling_metrics(self):
        """CouplingMetricsの作成テスト。"""
        metrics = CouplingMetrics(
            module_path="test/module.py",
            afferent_coupling=3,
            efferent_coupling=2,
            instability=0.4,
            lines_of_code=150,
        )

        self.assertEqual(metrics.module_path, "test/module.py")
        self.assertEqual(metrics.afferent_coupling, 3)
        self.assertEqual(metrics.efferent_coupling, 2)
        self.assertEqual(metrics.instability, 0.4)
        self.assertEqual(metrics.lines_of_code, 150)

    def test_distance_from_main_sequence(self):
        """メインシーケンスからの距離の計算テスト。"""
        metrics = CouplingMetrics(
            module_path="test/module.py",
            afferent_coupling=3,
            efferent_coupling=2,
            instability=0.4,
            abstractness=0.3,
        )

        # |A + I - 1| = |0.3 + 0.4 - 1| = |0.7 - 1| = |-0.3| = 0.3
        expected_distance = 0.3
        self.assertAlmostEqual(metrics.distance_from_main_sequence, expected_distance)

    def test_category_classification(self):
        """カテゴリ分類のテスト。"""
        # stable: 安定・具象
        stable = CouplingMetrics(
            module_path="stable.py",
            afferent_coupling=5,
            efferent_coupling=1,
            instability=0.2,
            abstractness=0.1,
        )
        self.assertEqual(stable.category, "stable")

        # unstable: 不安定・抽象
        unstable = CouplingMetrics(
            module_path="unstable.py",
            afferent_coupling=1,
            efferent_coupling=5,
            instability=0.8,
            abstractness=0.7,
        )
        self.assertEqual(unstable.category, "unstable")

        # painful: 安定・抽象
        painful = CouplingMetrics(
            module_path="painful.py",
            afferent_coupling=5,
            efferent_coupling=1,
            instability=0.2,
            abstractness=0.8,
        )
        self.assertEqual(painful.category, "painful")

        # useless: 不安定・具象
        useless = CouplingMetrics(
            module_path="useless.py",
            afferent_coupling=1,
            efferent_coupling=5,
            instability=0.8,
            abstractness=0.1,
        )
        self.assertEqual(useless.category, "useless")


class TestProjectCouplingMetrics(unittest.TestCase):
    """ProjectCouplingMetricsクラスのテスト。"""

    def test_dependency_density_calculation(self):
        """依存関係密度の計算テスト。"""
        # 3モジュール、2つの依存関係の場合
        # 密度 = 2 / (3 * (3-1)) = 2 / 6 = 0.333
        module_metrics = [
            CouplingMetrics(
                module_path="a.py",
                afferent_coupling=0,
                efferent_coupling=1,
                instability=1.0,
            ),
            CouplingMetrics(
                module_path="b.py",
                afferent_coupling=1,
                efferent_coupling=1,
                instability=0.5,
            ),
            CouplingMetrics(
                module_path="c.py",
                afferent_coupling=1,
                efferent_coupling=0,
                instability=0.0,
            ),
        ]

        project_metrics = ProjectCouplingMetrics(
            project_path="/test",
            module_count=3,
            total_internal_dependencies=2,
            average_instability=0.5,
            max_afferent_coupling=1,
            max_efferent_coupling=1,
            module_metrics=module_metrics,
        )

        expected_density = 2 / (3 * 2)  # 2 / 6 = 0.333
        self.assertAlmostEqual(
            project_metrics.dependency_density, expected_density, places=3
        )

    def test_get_unstable_modules(self):
        """不安定モジュールの取得テスト。"""
        module_metrics = [
            CouplingMetrics(
                module_path="stable.py",
                afferent_coupling=5,
                efferent_coupling=1,
                instability=0.2,
            ),
            CouplingMetrics(
                module_path="unstable.py",
                afferent_coupling=1,
                efferent_coupling=5,
                instability=0.8,
            ),
            CouplingMetrics(
                module_path="very_unstable.py",
                afferent_coupling=0,
                efferent_coupling=5,
                instability=1.0,
            ),
        ]

        project_metrics = ProjectCouplingMetrics(
            project_path="/test",
            module_count=3,
            total_internal_dependencies=5,
            average_instability=0.67,
            max_afferent_coupling=5,
            max_efferent_coupling=5,
            module_metrics=module_metrics,
        )

        unstable_modules = project_metrics.get_unstable_modules(0.7)
        self.assertEqual(len(unstable_modules), 2)
        self.assertIn("unstable.py", [m.module_path for m in unstable_modules])
        self.assertIn("very_unstable.py", [m.module_path for m in unstable_modules])


class TestEnhancedImportAnalyzer(unittest.TestCase):
    """EnhancedImportAnalyzerクラスのテスト。"""

    def setUp(self):
        """テスト用のセットアップ。"""
        self.project_root = Path("/tmp/test_project")
        self.module_path = Path("/tmp/test_project/src/module.py")

    def test_analyze_simple_imports(self):
        """シンプルなインポートの分析テスト。"""
        code = """
import os
import sys
from pathlib import Path
from myproject.utils import helper
"""

        analyzer = EnhancedImportAnalyzer(self.project_root, self.module_path)
        tree = __import__("ast").parse(code)
        analyzer.visit(tree)

        dependency = analyzer.get_dependency_info(lines_of_code=4)

        self.assertIn("os", dependency.imported_modules)
        self.assertIn("sys", dependency.imported_modules)
        self.assertIn("pathlib", dependency.imported_modules)
        self.assertIn("myproject.utils", dependency.imported_modules)
        self.assertEqual(dependency.lines_of_code, 4)

    def test_categorize_imports(self):
        """インポートの内部/外部分類テスト。"""
        # モックファイルシステムを作成
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)
            module_path = project_root / "src" / "module.py"

            # テスト用の内部モジュールを作成
            internal_module_dir = project_root / "myproject"
            internal_module_dir.mkdir()
            (internal_module_dir / "__init__.py").touch()

            code = """
import os
from myproject import utils
from external_lib import something
"""

            analyzer = EnhancedImportAnalyzer(project_root, module_path)
            tree = __import__("ast").parse(code)
            analyzer.visit(tree)

            dependency = analyzer.get_dependency_info()

            # myprojectは内部モジュールとして検出されるべき
            self.assertIn("myproject", dependency.internal_imports)
            # osとexternal_libは外部として検出されるべき
            self.assertIn("os", dependency.external_imports)
            self.assertIn("external_lib", dependency.external_imports)


class TestCouplingAnalyzer(unittest.TestCase):
    """CouplingAnalyzerクラスのテスト。"""

    def test_instability_calculation(self):
        """不安定度計算のテスト。"""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)
            analyzer = CouplingAnalyzer(project_root)

            # Ca=3, Ce=2の場合、I = Ce/(Ca+Ce) = 2/5 = 0.4
            instability = analyzer._calculate_instability(3, 2)
            self.assertAlmostEqual(instability, 0.4)

            # Ca=0, Ce=0の場合、I = 0
            instability = analyzer._calculate_instability(0, 0)
            self.assertAlmostEqual(instability, 0.0)

    def test_normalize_module_path(self):
        """モジュールパス正規化のテスト。"""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)
            analyzer = CouplingAnalyzer(project_root)

            # .pyサフィックスの除去
            normalized = analyzer._normalize_module_path("src/module.py")
            self.assertEqual(normalized, "src.module")

            # __init__.pyの処理
            normalized = analyzer._normalize_module_path("src/package/__init__.py")
            self.assertEqual(normalized, "src.package")

    def test_module_matching(self):
        """モジュールマッチングのテスト。"""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)
            analyzer = CouplingAnalyzer(project_root)

            # 完全一致
            self.assertTrue(analyzer._is_module_match("mymodule", "mymodule"))

            # パッケージマッチ
            self.assertTrue(
                analyzer._is_module_match("mypackage", "mypackage.submodule")
            )

            # サブモジュールマッチ
            self.assertTrue(
                analyzer._is_module_match("mypackage.submodule", "mypackage")
            )

            # 不一致
            self.assertFalse(analyzer._is_module_match("module1", "module2"))


class TestAnalyzeProjectCoupling(unittest.TestCase):
    """analyze_project_coupling関数のテスト。"""

    def test_analyze_project_coupling_integration(self):
        """プロジェクト全体の結合度分析の統合テスト。"""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)

            # テスト用のPythonファイルを作成
            module1 = project_root / "module1.py"
            module1.write_text(
                """
import os
from module2 import helper

def main():
    return helper()
"""
            )

            module2 = project_root / "module2.py"
            module2.write_text(
                """
import sys

def helper():
    return "hello"
"""
            )

            # 分析実行
            project_metrics = analyze_project_coupling(project_root)

            # 結果の検証
            self.assertIsInstance(project_metrics, ProjectCouplingMetrics)
            self.assertTrue(project_metrics.module_count > 0)

            # 各モジュールのメトリクスが含まれていることを確認
            module_paths = [m.module_path for m in project_metrics.module_metrics]
            self.assertTrue(any("module1.py" in path for path in module_paths))
            self.assertTrue(any("module2.py" in path for path in module_paths))

            # 依存関係が正しく検出されていることを確認
            self.assertTrue(project_metrics.total_internal_dependencies > 0)

    def test_analyze_empty_project(self):
        """空のプロジェクトの分析テスト。"""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)

            # 空のディレクトリで分析実行
            project_metrics = analyze_project_coupling(project_root)

            # 結果の検証
            self.assertEqual(project_metrics.module_count, 0)
            self.assertEqual(project_metrics.total_internal_dependencies, 0)
            self.assertEqual(project_metrics.average_instability, 0.0)

    @patch("pycodemetrics.metrics.coupling.CouplingAnalyzer")
    def test_analyze_project_coupling_with_exception(self, mock_analyzer_class):
        """例外発生時の処理テスト。"""
        # CouplingAnalyzerが例外を発生させるようにモック
        mock_analyzer = Mock()
        mock_analyzer.analyze_project.side_effect = Exception("Test exception")
        mock_analyzer_class.return_value = mock_analyzer

        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)

            # 例外が発生しても空のメトリクスが返されることを確認
            project_metrics = analyze_project_coupling(project_root)
            self.assertEqual(project_metrics.module_count, 0)
            self.assertEqual(project_metrics.total_internal_dependencies, 0)


class TestComplexScenarios(unittest.TestCase):
    """複雑なシナリオのテスト。"""

    def test_circular_dependencies(self):
        """循環依存のテスト。"""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)

            # 循環依存を持つモジュールを作成
            module_a = project_root / "module_a.py"
            module_a.write_text(
                """
from module_b import func_b

def func_a():
    return func_b()
"""
            )

            module_b = project_root / "module_b.py"
            module_b.write_text(
                """
from module_a import func_a

def func_b():
    return "result"
"""
            )

            # 分析実行
            project_metrics = analyze_project_coupling(project_root)

            # 循環依存が検出されることを確認
            self.assertEqual(project_metrics.module_count, 2)
            self.assertEqual(project_metrics.total_internal_dependencies, 2)

            # 両方のモジュールが適度な結合度を持つことを確認
            for module in project_metrics.module_metrics:
                self.assertTrue(module.efferent_coupling > 0)

    def test_large_project_structure(self):
        """大規模プロジェクト構造のテスト。"""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)

            # パッケージ構造を作成
            (project_root / "core").mkdir()
            (project_root / "core" / "__init__.py").touch()
            (project_root / "utils").mkdir()
            (project_root / "utils" / "__init__.py").touch()

            # コアモジュール（低結合）
            core_engine = project_root / "core" / "engine.py"
            core_engine.write_text("def process(): pass")

            # ユーティリティモジュール（高結合）
            utils_helper = project_root / "utils" / "helper.py"
            utils_helper.write_text(
                """
import os
import sys
from pathlib import Path
from core.engine import process

def helper_func():
    return process()
"""
            )

            # メインモジュール
            main = project_root / "main.py"
            main.write_text(
                """
from core.engine import process
from utils.helper import helper_func

def main():
    return helper_func()
"""
            )

            # 分析実行
            project_metrics = analyze_project_coupling(project_root)

            # 結果の検証
            self.assertTrue(project_metrics.module_count >= 3)
            self.assertTrue(project_metrics.total_internal_dependencies > 0)

            # engine.pyは高い入力結合度を持つべき
            engine_metrics = next(
                (
                    m
                    for m in project_metrics.module_metrics
                    if "engine.py" in m.module_path
                ),
                None,
            )
            self.assertIsNotNone(engine_metrics)
            self.assertTrue(engine_metrics.afferent_coupling > 0)


if __name__ == "__main__":
    unittest.main()
