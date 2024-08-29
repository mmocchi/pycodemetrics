from pycodemetrics.metrics.py.raw.radon_wrapper import (
    get_complexity,
    get_maintainability_index,
)


def test_get_maintainability_index():
    # Arrange
    code = """
def simple_function():
    pass
"""
    # Act
    result = get_maintainability_index(code)

    # Assert
    assert isinstance(result, float)
    assert result > 0  # Maintainability Index should be a positive float


def test_get_complexity():
    # Arrange
    code = """
def simple_function():
    pass
"""
    # Act
    result = get_complexity(code)

    # Assert
    assert isinstance(result, int)
    assert result == 1  # Simple function should have a complexity of 1

    # Arrange
    complex_code = """
def complex_function():
    if True:
        for i in range(10):
            print(i)
"""
    # Act
    result = get_complexity(complex_code)

    # Assert
    assert isinstance(result, int)
    assert result > 1  # Complex function should have a higher complexity
