import ast

from cognitive_complexity.api import get_cognitive_complexity
from pydantic import BaseModel


class FunctionCognitiveComplexity(BaseModel, frozen=True):
    """
    関数の認知的複雑度を表すデータクラス。

    このクラスは、特定の関数の認知的複雑度を計算し、その結果を保持します。
    認知的複雑度は、コードの理解や保守の難易度を示す指標です。

    Attributes:
        function_name (str): 関数名。
        complexity (int): 関数の認知的複雑度。
    """

    function_name: str
    complexity: int


def get_function_cognitive_complexity(
    code: str,
) -> list[FunctionCognitiveComplexity]:
    """
    指定されたコードの関数ごとの認知的複雑度を計算します。

    この関数は、提供されたコード文字列を解析し、各関数の認知的複雑度を計算します。
    結果は、各関数の認知的複雑度を含むオブジェクトのリストとして返されます。

    Args:
        code (str): 分析するソースコードを含む文字列。

    Returns:
        list[FunctionCognitiveComplexity]: 各関数の認知的複雑度を含むオブジェクトのリスト。
    """
    tree = ast.parse(code)

    funcdefs = (
        n
        for n in ast.walk(tree)
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
    )

    results = []
    for funcdef in funcdefs:
        complexity = get_cognitive_complexity(funcdef)
        results.append(
            FunctionCognitiveComplexity(
                function_name=funcdef.name, complexity=complexity
            )
        )
    return results
