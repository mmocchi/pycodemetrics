import ast
from dataclasses import dataclass

from cognitive_complexity.api import get_cognitive_complexity


@dataclass
class FunctionCognitiveComplexity:
    function_name: str
    complexity: int


def get_function_cognitive_complexity(
    code: str,
) -> list[FunctionCognitiveComplexity]:
    """
    Compute the cognitive complexity of a code snippet.
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
        results.append(FunctionCognitiveComplexity(funcdef.name, complexity))
    return results
