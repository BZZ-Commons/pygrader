import json
import os
import sys
from dataclasses import dataclass
from io import StringIO

import pytest
from _pytest.config import ExitCode

from utils import bcolors


def run_pytest():
    cases_list = load_cases()
    results = initialize_results()
    total_points = 0
    total_max = 0
    args = [
        '-k',
        '',
        '--disable-warnings', # --disable-warnings is used to suppress warnings from py_test.py
        '-q',
        '',
        '--timeout_method=signal' # --signal is used to timeout single unit-test
    ]


    print_header(cases_list)

    passed_cases = 0
    for casenum, case in enumerate(cases_list):
        result = initialize_case_result(case)
        args[1] = case.function
        args[4] = f'--timeout={case.timeout}'

        with Capturing() as output:
            exitcode = pytest.main(args)
        if exitcode == ExitCode.OK:
            passed_cases += 1
            summary = output[len(output) - 1]
            if 'passed' in summary:
                result['feedback'] = 'Success'
                result['points'] = case.points
                print_test_header(case.name, casenum + 1, len(cases_list), status="passed")
            elif 'xfailed' in summary:
                result['feedback'] = 'Success: Fails as expected'
                result['points'] = case.points
                print_test_header(case.name, casenum + 1, len(cases_list), status="passed")
            elif 'skipped' in summary:
                result['feedback'] = 'Test was skipped at this time'
                print_test_header(case.name, casenum + 1, len(cases_list), status="skipped")

        elif exitcode == ExitCode.TESTS_FAILED:
            print_test_header(case.name, casenum + 1, len(cases_list), status="failed")
            print(f'{bcolors.FAIL}{extract_error_message(output, result)}{bcolors.ENDC}')


        elif exitcode == ExitCode.NO_TESTS_COLLECTED:
            result['feedback'] = 'This test was not executed, maybe the name was wrong?'
            print_test_header(case.name, casenum + 1, len(cases_list), status="not_run")
        else:
            result['feedback'] = f'Unknown error "{exitcode}", check GitHub Actions for details'
            print(
                f'{bcolors.FAIL} Failed to get ExitCode.OK or ExitCode.TESTS_FAILED; exitcode={exitcode} {bcolors.ENDC}'
            )
            print(f'{bcolors.FAIL} {output} {bcolors.ENDC}')

        total_points += result['points']
        total_max += result['max']
        results['feedback'].append(result)
    results['points'] = total_points
    results['max'] = total_max
    print('\n')
    print(
        f'{bcolors.OKCYAN}{bcolors.BOLD}🏆 Grand total tests passed: {passed_cases}/{len(cases_list)}{bcolors.ENDC}'
    )
    print(
        f'{bcolors.OKCYAN}{bcolors.BOLD}🏆 Points: {total_points:.2f}/{total_max:.2f}{bcolors.ENDC}'
    )

    return results


def print_header(cases_list):
    print(
        f'{bcolors.HEADER}################################################################################{bcolors.ENDC}'
    )
    print(
        f'{bcolors.BOLD}{bcolors.HEADER}Running {len(cases_list)} Tests{bcolors.ENDC}'
    )
    print(
        f'{bcolors.HEADER}################################################################################{bcolors.ENDC}'
    )


def print_test_header(test_name, current, total, status):
    if status == "passed":
        color = bcolors.OKGREEN
        icon = "✅"
        message = "Test Passed"
    elif status == "failed":
        color = bcolors.FAIL
        icon = "❌"
        message = "Test Failed"
    elif status == "skipped":
        color = bcolors.WARNING  # Assuming you have yellow color for warnings.
        icon = "💤"
        message = "Skipped Test"
    elif status == 'not_run':
        color = bcolors.FAIL
        icon = '⛔'
        message = 'Test not run, contact your teacher'
    else:
        color = bcolors.FAIL
        icon = "❌"
        message = "Unknown Status"

    print('\n\n')
    print(
        f'{color}################################################################################{bcolors.ENDC}'
    )
    print(
        f'{color}{icon} {message}: {test_name} {current}/{total}{bcolors.ENDC}'
    )
    print(
        f'{color}################################################################################{bcolors.ENDC}'
    )


def extract_error_message(output, result) -> None:
    """Extract assertion failure details from the pytest output."""
    msg = ''
    assertion_error = next((line for line in output if 'Comparing values:' in line), None)

    if assertion_error:
        index = output.index(assertion_error)
        result['feedback'] = 'Assertion Error'
        # Use default 'N/A' if indices are out of range
        result['expected'] = output[index + 1].split(':', 1)[1].strip() if index + 1 < len(output) else 'N/A'
        result['actual'] = output[index + 2].split(':', 1)[1].strip() if index + 2 < len(output) else 'N/A'
        msg += f'Expected :\t {result["expected"]}\n'
        msg += f'Actual :\t {result["actual"]}\n'
    else:
        try:
            details = output[-2].split('-')[1].strip()
            result['feedback'] = f'Test failed - {details}'
            msg += f'Test failed - {details}'
        except:
            #msg = "Test failed:\n" + "\n".join(output)
            result['feedback'] = 'Test failed, check GitHub Actions for more details.'

    return msg


def load_cases() -> list:
    """
    Loads all test cases from the JSON file specified in the environment.
    :return: a list of test cases to be run
    """
    file_unittest = os.environ['FILE_UNITTESTS']
    cases = load_file(f'./.github/autograding/{file_unittest}')
    cases_list = (
        [
            Testcase(
                name=item['name'],
                function=item['function'],
                timeout=item['timeout'],
                points=item['points'],
            )
            for item in cases
        ]
        if cases
        else []
    )
    return cases_list


def initialize_results():
    """Initialize the results dictionary."""
    return {'category': 'pytest', 'points': 0, 'max': 0, 'feedback': []}


def initialize_case_result(case):
    """Initialize the result dictionary for an individual test case."""
    return {
        'name': case.name,
        'feedback': '',
        'expected': '',
        'actual': '',
        'points': 0,
        'max': case.points,
    }


def load_file(filepath: str) -> dict:
    """
    Utility function to load JSON data from a file.
    :param filepath: Path to the JSON file.
    :return: Parsed JSON data as a dictionary, or an empty dictionary if the file is not found.
    """
    try:
        with open(filepath, encoding='UTF-8') as file:
            return json.load(file)
    except IOError:
        print(f'File {filepath} not found')
        return {}


@dataclass
class Testcase:
    """
    Definition of a test case
    """

    name: str
    function: str
    timeout: int
    points: float


class Capturing(list):
    """
    Captures the output to stdout and stderr
    """

    def __enter__(self):
        self._stdout = sys.stdout
        sys.stdout = self._stringio = StringIO()
        return self

    def __exit__(self, *args):
        self.extend(self._stringio.getvalue().splitlines())
        del self._stringio  # free up some memory
        sys.stdout = self._stdout


if __name__ == '__main__':
    pass
