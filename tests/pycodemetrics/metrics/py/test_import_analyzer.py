import ast

from pycodemetrics.metrics.py.import_analyzer import (
    ImportAnalyzer,
    analyze_import_counts,
)


def test_analyze_import_counts():
    """
    analyze_import_counts関数のテスト。
    複数のimport文を含むコードを解析し、正しいインポート数を返すことを確認する。
    """
    # Arrange: テスト用のPythonコードを準備
    code = """
import os
import sys
from collections import defaultdict
from math import sqrt
import ast
"""

    # Act: analyze_import_counts関数を実行
    result = analyze_import_counts(code)

    # Assert: 期待されるインポート数と結果を比較
    assert result == 5


def test_import_analyzer():
    """
    ImportAnalyzerクラスのテスト。
    import文とfrom ... import文を正しく解析し、インポートされたモジュール名をリストとして返すことを確認する。
    """
    # Arrange: テスト用のPythonコードを準備
    code = """
import os
import sys
from collections import defaultdict
from math import sqrt
"""
    tree = ast.parse(code)
    analyzer = ImportAnalyzer()

    # Act: ASTを訪問してインポートを解析
    analyzer.visit(tree)
    imports = analyzer.get_imports()

    # Assert: 期待されるインポートリストと結果を比較
    assert imports == ["os", "sys", "collections.defaultdict", "math.sqrt"]
