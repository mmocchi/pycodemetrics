import ast

from cognitive_complexity.api import get_cognitive_complexity


def compute_cognitive_complexity(file_path: str) -> None:
    """
    Compute the cognitive complexity of a code snippet.
    """

    with open(file_path, "r") as f:
        code = f.read()

    tree = ast.parse(code)

    funcdefs = (
        n
        for n in ast.walk(tree)
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
    )
    for funcdef in funcdefs:
        complexity = get_cognitive_complexity(funcdef)
        print(funcdef.name, complexity)
