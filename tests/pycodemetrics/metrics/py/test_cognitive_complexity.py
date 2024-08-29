from pycodemetrics.metrics.py.cognitive_complexity import get_cognitive_complexity


def test_get_cognitive_complexity():
    # Arrange
    code = """
def example_function():
    if True:
        return 1
    else:
        return 0
    """

    # Act
    result = get_cognitive_complexity(code)

    # Assert
    expected_complexity = 2
    assert result == expected_complexity


def test_get_cognitive_complexity_multi_functions():
    # Arrange
    code = """
def example_function():
    if True:
        return 1
    else:
        return 0

def example_seconds_function():
    if True:
        return 1
    return 0
    """

    # Act
    result = get_cognitive_complexity(code)

    # Assert
    expected_complexity = 3
    assert result == expected_complexity


def test_get_cognitive_complexity_class_and_method():
    # Arrange
    code = """
class ExampleClass:
    def __init__(self):
        pass

    def example_function(self):
        if True:
            return 1
        else:
            return 0

    def example_seconds_function(self):
        if True:
            return 1
        return 0
    """

    # Act
    result = get_cognitive_complexity(code)

    # Assert
    expected_complexity = 3
    assert result == expected_complexity
