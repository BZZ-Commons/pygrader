"""
The `conftest.py` file is included to define custom pytest hooks that alter the default behavior of pytest.
Specifically, the `pytest_assertrepr_compare` function is defined within `conftest.py` to customize the
representation of assertion errors when comparing values. This customization helps in capturing and displaying
the expected and actual values in a more readable and detailed format during test failures.

The `pytest_assertrepr_compare` function works as follows:
- It takes the comparison operator (`op`), the left value (`left`), and the right value (`right`) as arguments.
- When an assertion fails, pytest uses this hook to format the output, which makes it easier to capture and analyze
  the specific values involved in the failed assertion.

By defining this function in `conftest.py`, the custom assertion representation is applied globally to all test
cases within the project. This ensures that any assertion error will display the expected and actual values
in a consistent and informative manner, facilitating better debugging and result reporting.

Usage:
- Place the `conftest.py` file in the root directory of your test suite or in any subdirectory where you want
  the custom hooks to be applied.
- Run your pytest-based tests as usual, and the custom assertion representation will be automatically utilized.
"""

def pytest_assertrepr_compare(op, left, right):
    return [
        "XXXXComparing values:XXXX",
        f"   expected: {left}",
        f"   actual  : {right}",
    ]
