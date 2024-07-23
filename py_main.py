import os
import urllib

import requests

from py_lint import py_lint
from py_test import py_test


def main():
    TARGET_URL = os.environ['TARGET_URL']
    TOKEN = os.getenv('TOKEN')
    FUNCTION = os.environ['FUNCTION']
    USERNAME = os.environ['USERNAME']
    SERVER = os.environ['SERVER']
    REPOPATH = os.environ['REPO']
    FILE_UNITTESTS = os.environ['FILE_UNITTESTS']
    FILE_LINT = os.environ['FILE_LINT']

    print(
        f'TARGET_URL={TARGET_URL}, TOKEN={TOKEN}, FUNCTION={FUNCTION}, USERNAME={USERNAME}, SERVER={SERVER}, REPO={REPOPATH}')
    repository = REPOPATH.split('/')[1]
    assignment = repository.removesuffix('-' + USERNAME)

    result = collect_results()
    update_moodle(
        result=result,
        target_url='https://moodle.it.bzz.ch/moodle',
        token=TOKEN,
        function=FUNCTION,
        user_name=USERNAME,
        assignment=assignment,
        external_link=f'{SERVER}/{REPOPATH}'
    )


def collect_results() -> dict:
    """
    collects the results from all grading modules
    :return:
    """
    result = {
        'points': 0.0,
        'max': 0.0,
        'feedback': ''
    }

    # Pytest
    testresults = py_test()
    result['points'] += testresults['points']
    result['max'] += testresults['max']
    result['feedback'] += wrap_feedback_table(testresults, 'Unittests')
    # Pylint
    testresults = py_lint()
    result['points'] += testresults['points']
    result['max'] += testresults['max']
    result['feedback'] += wrap_feedback_table(testresults, 'Linting')

    result['points'] = round(result['points'], 2)
    return result

def wrap_feedback_table(testresults: dict, title: str) -> str:
    """
    Adds a title to the feedback table and a total for the points
    :param feedback: Feedback table
    :param title: Title of the feedback
    :return:
    """

    feedback = f'#{title}'
    feedback += '\n'
    feedback += markdown_out(testresults['feedback'])
    feedback += '\n'
    feedback += f'**{testresults["points"]:.2f}/{testresults["max"]:.2f} Punkte**'
    feedback += '\n***\n'
    return feedback


def markdown_out(results: dict) -> str:
    """
    creates a markdown table from the results
    :param results:
    :return:
    """
    #if results is empty return string
    if not results:
        return ''

    # Extract headers
    headers = list(results[0].keys())

    # Start the table with headers

    table = '| ' + ' | '.join(headers) + ' |\n'
    table += '| ' + ' | '.join(['---'] * len(headers)) + ' |\n'

    # Add the rows
    for entry in results:
        row = [str(entry[header]) for header in headers]
        table += '| ' + ' | '.join(row) + ' |\n'

    return table

def update_moodle(
        result: dict,
        target_url: str,
        token: str,
        function: str,
        user_name: str,
        assignment: str,
        external_link: str
) -> None:
    """
    calls the webservice to update the assignment in moodle
    :param result:
    :param target_url:
    :param token:
    :param function:
    :param user_name:
    :param assignment:
    :param external_link:
    :return:
    """
    url = f'{target_url}/webservice/rest/server.php/?wstoken={token}&wsfunction={function}'
    feedback = urllib.parse.quote(result['feedback'])
    payload = {
        'assignment_name': assignment,
        'user_name': user_name,
        'points': result['points'],
        'max': result['max'],
        'externallink': external_link,
        'feedback': feedback
    }
    print(url)
    print(payload)
    response = requests.post(url=url, data=payload, timeout=30)
    print(response)
    print(response.text)


if __name__ == '__main__':
    from dotenv import load_dotenv

    # loading variables from .env file
    load_dotenv()
    main()
