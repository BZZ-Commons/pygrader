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
    args = ['-k', '']
    for case in cases_list:
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
            exitcode = pytest.main(args)
        if exitcode == ExitCode.OK:
            summary = output[len(output) - 1]
            if 'passed' in summary:
                result['feedback'] = 'Success'
                result['points'] = case.points
            elif 'xfailed' in summary:
                result['feedback'] = 'Success: Fails as expected'
                result['points'] = case.points
            elif 'skipped' in summary:
                result['feedback'] = 'Test was skipped at this time'
        elif exitcode == ExitCode.TESTS_FAILED:
            extract_assertion(output, result)
            print('assert fail')
        else:
            result['feedback'] = 'Unknown error, check GitHub Actions for details'
            print('Fail')

        total_points += result['points']
        total_max += result['max']
        results['feedback'].append(result)
    results['points'] = total_points
    results['max'] = total_max

    return results


def extract_assertion(message, result) -> None:
    for index, line in enumerate(message):
        if 'AssertionError:' in line:
            parts = line.split('AssertionError:', 1)
            result['feedback'] = 'Assertion Error: ' + parts[1]
            result['expected'] = message[index + 1]
            result['actual'] = message[index + 2]
            break


def load_cases() -> list:
    """
    loads all test cases
    :return: a list of testcases to be run
    :rtype: none
    """
    cases_list = list()

    FILE_UNITTESTS = os.environ['FILE_UNITTESTS']

    try:
        with open(f'./.github/autograding/{FILE_UNITTESTS}', encoding='UTF-8') as file:
            cases = json.load(file)
            for item in cases:
                testcase = Testcase(
                    name=item['name'],
                    function=item['function'],
                    timeout=item['timeout'],
                    points=item['points']
                )
                cases_list.append(testcase)
    except IOError as ex:
        print(f'file {FILE_UNITTESTS} not found')
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

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def function(self):
        return self._function

    @function.setter
    def function(self, value):
        self._function = value

    @property
    def timeout(self):
        return self._timeout

    @timeout.setter
    def timeout(self, value):
        self._timeout = value

    @property
    def points(self):
        return self._points

    @points.setter
    def points(self, value):
        self._points = value


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


if __name__ == '__main__':
    pass
