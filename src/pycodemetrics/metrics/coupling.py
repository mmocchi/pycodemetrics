"""モジュール結合度分析モジュール。

このモジュールは、Pythonプロジェクト内のモジュール間の結合度を分析します。
プロジェクト全体の構造的メトリクスを提供し、アーキテクチャの品質評価を行います。

主な機能:
    - プロジェクト全体の依存関係収集
    - Afferent Coupling (Ca) - 入力結合度の計算
    - Efferent Coupling (Ce) - 出力結合度の計算
    - Instability (I) - 不安定度の計算
    - Abstractness (A) - 抽象度の計算（将来実装）
    - モジュール間の依存関係グラフ構築

結合度メトリクスの解釈:
    - Ca (入力結合度): このモジュールに依存するモジュール数。高いほど重要で安定
    - Ce (出力結合度): このモジュールが依存するモジュール数。高いほど複雑
    - I (不安定度): Ce / (Ca + Ce)。1に近いほど変更の影響を受けやすい
    - A (抽象度): 抽象クラス・インターフェースの割合（将来実装）

制限事項:
    - Pythonファイルのみを対象とします
    - 動的インポートは検出できません
    - 現在は抽象度の計算は未実装です
"""

import ast
from pathlib import Path
from typing import Dict, List, Optional

from pydantic import BaseModel, computed_field


class ModuleDependency(BaseModel, frozen=True, extra="forbid"):
    """モジュールの依存関係を表すクラス。

    Attributes:
        module_path (str): プロジェクトルートからの相対モジュールパス
        imported_modules (List[str]): このモジュールがインポートするモジュールのリスト
        internal_imports (List[str]): プロジェクト内部のインポートのみ
        external_imports (List[str]): 外部ライブラリのインポート
        lines_of_code (int): このモジュールの行数
    """

    module_path: str
    imported_modules: List[str]
    internal_imports: List[str]
    external_imports: List[str]
    lines_of_code: int = 0


class CouplingMetrics(BaseModel, frozen=True, extra="forbid"):
    """モジュール結合度メトリクスを表すクラス。

    Attributes:
        module_path (str): 対象モジュールのパス
        afferent_coupling (int): 入力結合度 - このモジュールに依存するモジュール数
        efferent_coupling (int): 出力結合度 - このモジュールが依存するモジュール数
        instability (float): 不安定度 = Ce / (Ca + Ce)
        abstractness (float): 抽象度（将来実装予定）
        lines_of_code (int): このモジュールの行数
        category (str): モジュールのカテゴリ（stable, unstable, painful, useless）
    """

    module_path: str
    afferent_coupling: int
    efferent_coupling: int
    instability: float
    abstractness: float = 0.0
    lines_of_code: int = 0

    @computed_field(return_type=float)  # type: ignore
    @property
    def distance_from_main_sequence(self) -> float:
        """メインシーケンスからの距離 = |A + I - 1|

        理想的なアーキテクチャでは、モジュールはメインシーケンス（A + I = 1）上に位置する。
        この値が小さいほど良い設計とされる。
        """
        return abs(self.abstractness + self.instability - 1)

    @computed_field(return_type=str)  # type: ignore
    @property
    def category(self) -> str:
        """モジュールのカテゴリを判定

        Returns:
            str: stable, unstable, painful, useless のいずれか
        """
        if self.instability < 0.5 and self.abstractness < 0.5:
            return "stable"  # 安定・具象（理想的なユーティリティ）
        elif self.instability >= 0.5 and self.abstractness >= 0.5:
            return "unstable"  # 不安定・抽象（理想的なインターフェース）
        elif self.instability < 0.5 and self.abstractness >= 0.5:
            return "painful"  # 安定・抽象（変更困難）
        else:
            return "useless"  # 不安定・具象（価値の低い）

    def to_dict(self) -> dict:
        return self.model_dump()

    @classmethod
    def get_keys(cls):
        return cls.model_fields.keys()


class ProjectCouplingMetrics(BaseModel, frozen=True, extra="forbid"):
    """プロジェクト全体の結合度メトリクスを表すクラス。

    Attributes:
        project_path (str): プロジェクトのパス
        module_count (int): 解析対象モジュール数
        total_internal_dependencies (int): 内部依存関係の総数
        average_instability (float): 平均不安定度
        max_afferent_coupling (int): 最大入力結合度
        max_efferent_coupling (int): 最大出力結合度
        module_metrics (List[CouplingMetrics]): 各モジュールのメトリクス
    """

    project_path: str
    module_count: int
    total_internal_dependencies: int
    average_instability: float
    max_afferent_coupling: int
    max_efferent_coupling: int
    module_metrics: List[CouplingMetrics]

    @computed_field(return_type=float)  # type: ignore
    @property
    def dependency_density(self) -> float:
        """依存関係密度 = 総依存関係数 / (モジュール数 * (モジュール数 - 1))

        0に近いほど疎結合、1に近いほど密結合
        """
        if self.module_count <= 1:
            return 0.0
        max_dependencies = self.module_count * (self.module_count - 1)
        return self.total_internal_dependencies / max_dependencies

    def get_unstable_modules(self, threshold: float = 0.8) -> List[CouplingMetrics]:
        """不安定なモジュールを取得

        Args:
            threshold (float): 不安定度の閾値

        Returns:
            List[CouplingMetrics]: 閾値を超えるモジュールのリスト
        """
        return [m for m in self.module_metrics if m.instability > threshold]

    def get_stable_modules(self, threshold: float = 0.2) -> List[CouplingMetrics]:
        """安定したモジュールを取得

        Args:
            threshold (float): 不安定度の閾値

        Returns:
            List[CouplingMetrics]: 閾値未満のモジュールのリスト
        """
        return [m for m in self.module_metrics if m.instability < threshold]

    def get_high_coupling_modules(
        self, ca_threshold: int = 5, ce_threshold: int = 5
    ) -> List[CouplingMetrics]:
        """高結合なモジュールを取得

        Args:
            ca_threshold (int): 入力結合度の閾値
            ce_threshold (int): 出力結合度の閾値

        Returns:
            List[CouplingMetrics]: 閾値を超えるモジュールのリスト
        """
        return [
            m
            for m in self.module_metrics
            if m.afferent_coupling > ca_threshold or m.efferent_coupling > ce_threshold
        ]


class EnhancedImportAnalyzer(ast.NodeVisitor):
    """拡張されたインポート分析クラス。

    既存のImportAnalyzerを拡張し、より詳細な依存関係情報を収集します。
    プロジェクト内部と外部の依存関係を自動的に分類します。
    """

    def __init__(self, project_root: Path, current_module_path: Path):
        self.project_root = project_root
        self.current_module_path = current_module_path
        self.imports: List[str] = []
        self.internal_imports: List[str] = []
        self.external_imports: List[str] = []

    def visit_Import(self, node: ast.Import) -> None:
        """Import文を処理"""
        for alias in node.names:
            self.imports.append(alias.name)
            self._categorize_import(alias.name)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """ImportFrom文を処理"""
        if node.module:
            self.imports.append(node.module)
            self._categorize_import(node.module)

            for alias in node.names:
                full_name = f"{node.module}.{alias.name}"
                self.imports.append(full_name)
                self._categorize_import(node.module)  # モジュール部分のみで判定

    def _categorize_import(self, import_name: str) -> None:
        """インポートを内部/外部に分類"""
        # 相対インポートは内部とする
        if import_name.startswith("."):
            self.internal_imports.append(import_name)
            return

        # プロジェクトのルートパッケージ名から始まるかチェック
        project_name = self.project_root.name
        if import_name.startswith(project_name + ".") or import_name == project_name:
            self.internal_imports.append(import_name)
            return

        # プロジェクトルートからの相対パスで内部モジュールかチェック
        try:
            # プロジェクト内のモジュールパスに変換を試行
            potential_path = self.project_root / import_name.replace(".", "/")
            if (
                potential_path.with_suffix(".py").exists()
                or (potential_path / "__init__.py").exists()
            ):
                self.internal_imports.append(import_name)
                return
        except Exception:
            pass

        # デフォルトは外部
        self.external_imports.append(import_name)

    def get_dependency_info(self, lines_of_code: int = 0) -> ModuleDependency:
        """依存関係情報を取得"""
        return ModuleDependency(
            module_path=str(self.current_module_path.relative_to(self.project_root)),
            imported_modules=self.imports,
            internal_imports=list(set(self.internal_imports)),
            external_imports=list(set(self.external_imports)),
            lines_of_code=lines_of_code,
        )


class CouplingAnalyzer:
    """プロジェクト全体の結合度分析を行うクラス。

    プロジェクト内の全Pythonファイルを解析し、モジュール間の結合度を計算します。
    システム全体のアーキテクチャ品質を評価するためのメトリクスを提供します。
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.dependencies: Dict[str, ModuleDependency] = {}
        self.coupling_metrics: Dict[str, CouplingMetrics] = {}

    def analyze_project(
        self, exclude_patterns: Optional[List[str]] = None
    ) -> ProjectCouplingMetrics:
        """プロジェクト全体の結合度を分析

        Args:
            exclude_patterns (Optional[List[str]]): 除外するパターンのリスト

        Returns:
            ProjectCouplingMetrics: プロジェクト全体の結合度メトリクス
        """
        if exclude_patterns is None:
            exclude_patterns = ["__pycache__", ".git", ".pytest_cache", "node_modules"]

        # 1. 全Pythonファイルの依存関係を収集
        self._collect_all_dependencies(exclude_patterns)

        # 2. 各モジュールの結合度メトリクスを計算
        self._calculate_coupling_metrics()

        # 3. プロジェクト全体のメトリクスを計算
        return self._calculate_project_metrics()

    def _collect_all_dependencies(self, exclude_patterns: List[str]) -> None:
        """プロジェクト内の全Pythonファイルの依存関係を収集"""
        python_files = self._find_python_files(exclude_patterns)

        for python_file in python_files:
            try:
                with open(python_file, "r", encoding="utf-8") as f:
                    code = f.read()

                # 行数をカウント
                lines_of_code = len(
                    [line for line in code.splitlines() if line.strip()]
                )

                dependency = self._analyze_module_dependencies(
                    code, python_file, lines_of_code
                )
                self.dependencies[dependency.module_path] = dependency

            except (UnicodeDecodeError, IOError):
                # ファイル読み込みエラーは無視
                continue

    def _find_python_files(self, exclude_patterns: List[str]) -> List[Path]:
        """Pythonファイルを検索"""
        python_files = []

        for path in self.project_root.rglob("*.py"):
            # 除外パターンにマッチするパスをスキップ
            if any(pattern in str(path) for pattern in exclude_patterns):
                continue
            python_files.append(path)

        return python_files

    def _analyze_module_dependencies(
        self, code: str, module_path: Path, lines_of_code: int
    ) -> ModuleDependency:
        """モジュールの依存関係を分析"""
        try:
            tree = ast.parse(code)
            analyzer = EnhancedImportAnalyzer(self.project_root, module_path)
            analyzer.visit(tree)
            return analyzer.get_dependency_info(lines_of_code)
        except SyntaxError:
            # 構文エラーの場合は空の依存関係を返す
            return ModuleDependency(
                module_path=str(module_path.relative_to(self.project_root)),
                imported_modules=[],
                internal_imports=[],
                external_imports=[],
                lines_of_code=lines_of_code,
            )

    def _calculate_coupling_metrics(self) -> None:
        """各モジュールの結合度メトリクスを計算"""
        for module_path, dependency in self.dependencies.items():
            # Efferent Coupling (Ce) - このモジュールが依存するモジュール数
            efferent_coupling = len(dependency.internal_imports)

            # Afferent Coupling (Ca) - このモジュールに依存するモジュール数
            afferent_coupling = self._calculate_afferent_coupling(module_path)

            # Instability (I) - 不安定度
            instability = self._calculate_instability(
                afferent_coupling, efferent_coupling
            )

            self.coupling_metrics[module_path] = CouplingMetrics(
                module_path=module_path,
                afferent_coupling=afferent_coupling,
                efferent_coupling=efferent_coupling,
                instability=instability,
                lines_of_code=dependency.lines_of_code,
            )

    def _calculate_afferent_coupling(self, target_module: str) -> int:
        """指定モジュールの入力結合度を計算"""
        count = 0
        target_module_normalized = self._normalize_module_path(target_module)

        for module_path, dependency in self.dependencies.items():
            if module_path == target_module:
                continue

            # このモジュールが対象モジュールをインポートしているかチェック
            for imported in dependency.internal_imports:
                imported_normalized = self._normalize_module_path(imported)
                if self._is_module_match(imported_normalized, target_module_normalized):
                    count += 1
                    break

        return count

    def _normalize_module_path(self, module_path: str) -> str:
        """モジュールパスを正規化"""
        # ファイルパスからモジュール名に変換
        if module_path.endswith(".py"):
            module_path = module_path[:-3]
        if module_path.endswith("/__init__"):
            module_path = module_path[:-9]
        return module_path.replace("/", ".")

    def _is_module_match(self, imported_module: str, target_module: str) -> bool:
        """インポートされたモジュールが対象モジュールにマッチするかチェック"""
        # 両方のモジュールパスを正規化
        imported_normalized = self._normalize_module_path(imported_module)
        target_normalized = self._normalize_module_path(target_module)

        # 完全一致
        if imported_normalized == target_normalized:
            return True

        # パッケージとしてのマッチ (例: mypackage が mypackage.submodule をインポート)
        if target_normalized.startswith(imported_normalized + "."):
            return True

        # サブモジュールとしてのマッチ (例: mypackage.submodule が mypackage をインポート)
        if imported_normalized.startswith(target_normalized + "."):
            return True

        # パス形式での一致確認
        imported_parts = imported_module.split(".")
        target_parts = target_module.replace("/", ".").replace(".py", "").split(".")

        # 末尾一致チェック（プロジェクト名を除いた部分で比較）
        if len(imported_parts) >= 2 and len(target_parts) >= 1:
            imported_suffix = ".".join(imported_parts[1:])  # プロジェクト名を除く
            target_suffix = ".".join(target_parts)
            if imported_suffix == target_suffix:
                return True

        return False

    def _calculate_instability(
        self, afferent_coupling: int, efferent_coupling: int
    ) -> float:
        """不安定度を計算 I = Ce / (Ca + Ce)"""
        total_coupling = afferent_coupling + efferent_coupling
        if total_coupling == 0:
            return 0.0
        return efferent_coupling / total_coupling

    def _calculate_project_metrics(self) -> ProjectCouplingMetrics:
        """プロジェクト全体のメトリクスを計算"""
        module_metrics = list(self.coupling_metrics.values())

        if not module_metrics:
            return ProjectCouplingMetrics(
                project_path=str(self.project_root),
                module_count=0,
                total_internal_dependencies=0,
                average_instability=0.0,
                max_afferent_coupling=0,
                max_efferent_coupling=0,
                module_metrics=[],
            )

        total_dependencies = sum(
            len(dep.internal_imports) for dep in self.dependencies.values()
        )
        average_instability = sum(m.instability for m in module_metrics) / len(
            module_metrics
        )
        max_afferent = max(m.afferent_coupling for m in module_metrics)
        max_efferent = max(m.efferent_coupling for m in module_metrics)

        return ProjectCouplingMetrics(
            project_path=str(self.project_root),
            module_count=len(module_metrics),
            total_internal_dependencies=total_dependencies,
            average_instability=average_instability,
            max_afferent_coupling=max_afferent,
            max_efferent_coupling=max_efferent,
            module_metrics=module_metrics,
        )

    def get_dependency_graph(self) -> Dict[str, List[str]]:
        """依存関係グラフを取得"""
        graph = {}
        for module_path, dependency in self.dependencies.items():
            graph[module_path] = dependency.internal_imports
        return graph


def analyze_project_coupling(
    project_root: Path, exclude_patterns: Optional[List[str]] = None
) -> ProjectCouplingMetrics:
    """プロジェクト全体の結合度を分析する便利関数

    Args:
        project_root (Path): プロジェクトのルートディレクトリ
        exclude_patterns (Optional[List[str]]): 除外するパターンのリスト

    Returns:
        ProjectCouplingMetrics: プロジェクト全体の結合度メトリクス
    """
    try:
        analyzer = CouplingAnalyzer(project_root)
        return analyzer.analyze_project(exclude_patterns)
    except Exception:
        # 例外が発生した場合は空のメトリクスを返す
        return ProjectCouplingMetrics(
            project_path=str(project_root),
            module_count=0,
            total_internal_dependencies=0,
            average_instability=0.0,
            max_afferent_coupling=0,
            max_efferent_coupling=0,
            module_metrics=[],
        )
