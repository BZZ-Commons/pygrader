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
            #exitcode = pytest.main(args,plugins=["py_test"])
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
        else:
            result['feedback'] = 'Unknown error, check GitHub Actions for details'
            print('Failed to get ExitCode.OK or ExitCode.TESTS_FAILED')

        total_points += result['points']
        total_max += result['max']
        results['feedback'].append(result)
    results['points'] = total_points
    results['max'] = total_max

    return results


def extract_assertion(message, result) -> None:
    for index, line in enumerate(message):
        print(index,line)
        if 'AssertionError' in line:
            result['feedback'] = 'Assertion Error'
            result['expected'] = str.split(message[index - 2],':' ,1)[1].strip()
            result['actual'] = str.split(message[index - 3],':' ,1)[1].strip()
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


def pytest_exception_interactt(node, call, report):
    '''
    Diese Funktion wird aufgerufen, wenn ein Testfall fehlschlägt.
    '''
    print("\n\nSTART EXCEPTION INTERACT")
    exception = {
        'function': "",
        'call': "",
        'report': ""
    }

    if report.failed:
        print(str(call.excinfo.value))
        print(node.nodeid)
        # Extrahiere den fehlerhaften Code und den Testfall
        fehlerhafter_code = str(call.excinfo.value)
        testfall = node.nodeid
        exception['function'] = node.nodeid.split("::")[1]
        print(exception['function'])
        #print(str(call.excinfo.value))
        testfall = node.nodeid

        # Sende die Informationen an die API (Pseudocode)
        #sende_zu_chatgpt_api(fehlerhafter_code, testfall)
    print("END EXCEPTION INTERACT\n\n")

if __name__ == '__main__':
    pass
