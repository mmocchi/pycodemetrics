from pycodemetrics.metrics.py.raw.cc_wrapper import get_function_cognitive_complexity


def get_cognitive_complexity(code: str) -> int:
    cognitive_complexity = get_function_cognitive_complexity(code)
    return sum(c.complexity for c in cognitive_complexity)
