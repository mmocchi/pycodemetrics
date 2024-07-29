import ast


class ImportAnalyzer(ast.NodeVisitor):
    def __init__(self):
        self.imports = []

    def visit_Import(self, node):
        for alias in node.names:
            self.imports.append(alias.name)

    def visit_ImportFrom(self, node):
        for alias in node.names:
            self.imports.append(node.module + "." + alias.name)

    def get_imports(self):
        return self.imports


def analyze_import_counts(code) -> int:
    """
    指定されたコードのインポートの数をカウントします。

    Args:
        code (str): 分析するコード

    Returns:
        int: インポートの数
    """
    tree = ast.parse(code)
    analyzer = ImportAnalyzer()
    analyzer.visit(tree)
    return len(analyzer.get_imports())
