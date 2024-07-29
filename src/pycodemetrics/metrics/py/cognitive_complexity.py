from pycodemetrics.metrics.py.raw.cc_wrapper import get_function_cognitive_complexity


def get_cognitive_complexity(code: str) -> int:
    """
    指定されたコードの認知的複雑度を計算します。

    この関数は提供されたコード文字列の認知的複雑度を計算します。
    関数ごとに認知的複雑度を計算されたものを合計して返します。

    Args:
        code (str): 分析するソースコードを含む文字列。

    Returns:
        int: 提供されたコードの総認知的複雑度。
    """
    cognitive_complexity = get_function_cognitive_complexity(code)
    return sum(c.complexity for c in cognitive_complexity)
