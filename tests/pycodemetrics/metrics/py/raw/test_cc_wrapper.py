from pycodemetrics.metrics.py.raw.cc_wrapper import (
    FunctionCognitiveComplexity,
    get_function_cognitive_complexity,
)


def test_single_function():
    # Arrange
    code = """
def simple_function():
    pass
"""

    # Act
    result = get_function_cognitive_complexity(code)

    # Assert
    expected = [
        FunctionCognitiveComplexity(function_name="simple_function", complexity=0)
    ]
    assert result == expected


def test_nested_function():
    # Arrange
    code = """
def outer_function():
    def inner_function():
        pass

    if True:
        inner_function()
"""

    # Act
    result = get_function_cognitive_complexity(code)

    # Assert
    expected = [
        FunctionCognitiveComplexity(function_name="outer_function", complexity=1),
        FunctionCognitiveComplexity(function_name="inner_function", complexity=0),
    ]
    assert result == expected


def test_async_function():
    code = """
async def async_function():
    pass
"""
    expected = [
        FunctionCognitiveComplexity(function_name="async_function", complexity=0)
    ]
    result = get_function_cognitive_complexity(code)
    assert result == expected
