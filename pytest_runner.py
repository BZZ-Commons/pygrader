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
        '--disable-warnings',
        '-q',
    ]  # --disable-warnings is used to suppress warnings from py_test.py

    print_header(cases_list)

    passed_cases = 0
    for casenum, case in enumerate(cases_list):
        result = initialize_case_result(case)
        args[1] = case.function

        with Capturing() as output:
            exitcode = pytest.main(args)

        if exitcode == ExitCode.OK:
            passed_cases += 1
            summary = output[len(output) - 1]
            if 'passed' in summary:
                result['feedback'] = 'Success'
                result['points'] = case.points
                print_test_header(case.name, casenum + 1, len(cases_list), True)

            elif 'xfailed' in summary:
                result['feedback'] = 'Success: Fails as expected'
                result['points'] = case.points
                print_test_header(case.name, casenum + 1, len(cases_list), True)

            elif 'skipped' in summary:
                result['feedback'] = 'Test was skipped at this time'
                print_test_header(case.name, casenum + 1, len(cases_list), True)

        elif exitcode == ExitCode.TESTS_FAILED:
            result['feedback'] = 'Test failed, check GitHub Actions for details'
            print_test_header(case.name, casenum + 1, len(cases_list), False)
            extract_assertion(output, result)
        else:
            result['feedback'] = 'Unknown error, check GitHub Actions for details'
            print(
                f'{bcolors.FAIL} Failed to get ExitCode.OK or ExitCode.TESTS_FAILED {bcolors.ENDC}'
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


def print_test_header(test_name, current, total, passed):
    color = bcolors.OKGREEN if passed else bcolors.FAIL
    print('\n\n')
    print(
        f'{color}################################################################################{bcolors.ENDC}'
    )
    print(
        f'{color}{"✅" if passed else "❌"} Running test: {test_name} {current}/{total}{bcolors.ENDC}'
    )
    print(
        f'{color}################################################################################{bcolors.ENDC}'
    )


def extract_assertion(message, result) -> None:
    """Extract assertion failure details from the pytest output."""
    for index, line in enumerate(message):
        if 'Comparing values:' in line:
            result['feedback'] = 'Assertion Error'
            result['expected'] = message[index + 1].split(':', 1)[1].strip()
            print(f'{bcolors.FAIL}Expected :\t {result["expected"]}{bcolors.ENDC}')
            result['actual'] = message[index + 2].split(':', 1)[1].strip()
            print(f'{bcolors.FAIL}Actual :\t {result["actual"]}{bcolors.ENDC}')
            break


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
