import pytest

from pathlib import Path

from move_imports import main

root = Path(__file__).parent

@pytest.mark.parametrize("args, result_path", [
    ([f"{root}/example.py"], f"{root}/example_result.py"),
    ([f"{root}/example.py", "--isort"], f"{root}/example_result_with_isort.py"),
    ([f"{root}/example2.py"], f"{root}/example2_result.py"),
    ([f"{root}/example3.py", "--isort"], f"{root}/example3_result.py"),
])
def test_main(args, result_path):
    result = main(args + ["--show-only"], print_source=False)
    assert result == [Path(result_path).read_text()]