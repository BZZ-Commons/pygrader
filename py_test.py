""" This module is used to run pytest tests and return the results in a format that can be used by GitHub Actions
    to provide feedback to students. It loads test cases from a JSON file and runs each test case using pytest.
    The results are then collected and returned as a dictionary with the following keys
    - category: The category of the test
    - points: The points obtained
    - max: The maximum points
    - feedback: A list of feedback messages
    Each feedback message is a dictionary with the following keys
    - name: The name of the test
    - feedback: The feedback message
    - expected: The expected value (if applicable)
    - actual: The actual value (if applicable)
    - points: The points obtained
    - max: The maximum points for the test
    The points are calculated based on the test results as follows:
    - If the test passes, the student receives the maximum points for the test
    - If the test fails, the student receives 0 points for the test
    - If the test is skipped, the student receives 0 points for the test
    - If the test is marked as xfail, the student receives the maximum points for the test
    The total points are calculated by summing the points obtained from each test case.
    The maximum points are calculated by summing the maximum points from each test case.
"""

import json
import os
import sys
from dataclasses import dataclass
from io import StringIO

import pytest
from _pytest.config import ExitCode


def py_test():
    cases_list = load_cases()
    results = {
        'category': 'pytest',
        'points': 0,
        'max': 0,
        'feedback': []
    }
    total_points = 0
    total_max = 0
    args = ['-k', '','--disable-warnings', '-q'] #--disable-warnings is used to suppress warnings from py_test.py
    print(f'{bcolors.HEADER}################################################################################{bcolors.ENDC}')
    print(f'{bcolors.HEADER}Running {len(cases_list)} test cases{bcolors.ENDC}')
    print(f'{bcolors.HEADER}################################################################################{bcolors.ENDC}')
    passed_cases = 0
    for casenum, case in enumerate(cases_list):
        result = {
            'name': case.name,
            'feedback': '',
            'expected': '',
            'actual': '',
            'points': 0,
            'max': case.points
        }
        args[1] = case.function
        with Capturing() as output:
            print('\n\n')
            print('################################################################################')
            print(f'Running test: {case.name} {casenum + 1}/{len(cases_list)}')
            print('################################################################################')
            exitcode = pytest.main(args)
        if exitcode == ExitCode.OK:
            passed_cases += 1
            summary = output[len(output) - 1]
            if 'passed' in summary:
                result['feedback'] = 'Success'
                result['points'] = case.points
                for index, line in enumerate(output):
                    if index == 4:
                        line = '✅  ' + line
                    print(f"{bcolors.OKGREEN}{line}{bcolors.ENDC}")
            elif 'xfailed' in summary:
                result['feedback'] = 'Success: Fails as expected'
                result['points'] = case.points
                for index, line in enumerate(output):
                    if index == 4:
                        line = '✅  ' + line
                    print(f"{bcolors.OKGREEN}{line}{bcolors.ENDC}")
            elif 'skipped' in summary:
                result['feedback'] = 'Test was skipped at this time'
                for index, line in enumerate(output):
                    if index == 4:
                        line = '✅  ' + line
                    print(f"{bcolors.OKGREEN}{line}{bcolors.ENDC}")
        elif exitcode == ExitCode.TESTS_FAILED:
            result['feedback'] = 'Test failed, check GitHub Actions for details'
            extract_assertion(output, result)
        else:
            result['feedback'] = 'Unknown error, check GitHub Actions for details'
            print(f"{bcolors.FAIL}{'Failed to get ExitCode.OK or ExitCode.TESTS_FAILED'}{bcolors.ENDC}")

        total_points += result['points']
        total_max += result['max']
        results['feedback'].append(result)
    results['points'] = total_points
    results['max'] = total_max

    print(f'{bcolors.OKCYAN}{bcolors.BOLD}🏆 Grand total tests passed: {passed_cases}/{len(cases_list)}{bcolors.ENDC}')
    return results


def extract_assertion(message, result) -> None:
    for index, line in enumerate(message):
        if index == 4:
            line = '❌  ' + line
        print(f"{bcolors.FAIL}{line}{bcolors.ENDC}")
        if 'Comparing values:' in line:
            result['feedback'] = 'Assertion Error'
            result['expected'] = message[index + 1].split(':', 1)[1].strip()
            print(f'\t\t\t{bcolors.FAIL}Expected : {result["expected"]}{bcolors.ENDC}')
            result['actual'] = message[index + 2].split(':', 1)[1].strip()
            print(f'\t\t\t{bcolors.FAIL}Actual : {result["actual"]}{bcolors.ENDC}')
            print('\n\n')
            break

def load_cases() -> list:
    """
    loads all test cases
    :return: a list of testcases to be run
    :rtype: none
    """
    cases_list = list()

    file_unittest = os.environ['FILE_UNITTESTS']

    try:
        with open(f'./.github/autograding/{file_unittest}', encoding='UTF-8') as file:
            cases = json.load(file)
            for item in cases:
                testcase = Testcase(
                    name=item['name'],
                    function=item['function'],
                    timeout=item['timeout'],
                    points=item['points']
                )
                cases_list.append(testcase)
    except IOError:
        print(f'file {file_unittest} not found')
    return cases_list


@dataclass
class Testcase:
    """
    definition of a test case
    """
    name: str
    function: str
    timeout: int
    points: float

class Capturing(list):
    """
    captures the output to stdout and stderr
    """

    def __enter__(self):
        self._stdout = sys.stdout
        sys.stdout = self._stringio = StringIO()
        return self

    def __exit__(self, *args):
        self.extend(self._stringio.getvalue().splitlines())
        del self._stringio  # free up some memory
        sys.stdout = self._stdout

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


if __name__ == '__main__':
    pass
