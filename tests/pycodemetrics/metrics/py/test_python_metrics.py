import pytest
from pycodemetrics.metrics.py.python_metrics import (
    compute_metrics,
    PythonMetrics,
    get_product_or_test
)
@pytest.mark.parametrize(
    "filepath, expected",
    [
        ("src/main.py", "product"),
        ("test.py", "product"),
        ("tests/test_main.py", "test"),
        ("xxx/tests/unit/test_helper.py", "test"),
        ("abc/tests/helper.py", "test")
    ]
)
def test_get_product_or_test(filepath, expected):
    assert get_product_or_test(filepath) == expected
    
@pytest.fixture
def sample_python_file(tmp_path):
    file = tmp_path / "sample.py"
    file.write_text("""     
def hello():
    print("Hello, World!")

if __name__ == "__main__":
    hello()
    """)
    return file

def test_compute_metrics(sample_python_file):
    metrics = compute_metrics(str(sample_python_file))
    assert isinstance(metrics, PythonMetrics)
    assert metrics.lines_of_code > 0
    assert metrics.logical_lines_of_code > 0
    assert metrics.cyclomatic_complexity >= 1
    assert metrics.maintainability_index > 0
    assert metrics.cognitive_complexity >= 0
    assert metrics.product_or_test == "product"

