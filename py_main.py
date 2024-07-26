""" Main script for grading assignments"""

import os
import urllib.parse

import requests

from py_lint import py_lint
from py_test import py_test

DEBUG = True


def main():
    target_url = os.environ['TARGET_URL']
    token = os.getenv('TOKEN')
    function = os.environ['FUNCTION']
    username = os.environ['USERNAME']
    server = os.environ['SERVER']
    repo_path = os.environ['REPO']

    if DEBUG: print(
        f'TARGET_URL={target_url}, TOKEN={token}, FUNCTION={function}, '
        f'USERNAME={username}, SERVER={server}, REPO={repo_path}')

    repository = repo_path.split('/')[1]
    assignment = repository.removesuffix('-' + username)

    result = collect_results()
    update_moodle(
        result=result,
        target_url=target_url,
        token=token,
        function=function,
        user_name=username,
        assignment=assignment,
        external_link=f'{server}/{repo_path}'
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

    if DEBUG: print('######### FEEDBACK TABLES ######### ')
    if DEBUG: print(result['feedback'])

    return result


def wrap_feedback_table(testresults: dict, title: str) -> str:
    """
    Adds a title to the feedback table and a total for the points
    :param testresults: Testresults to wrap
    :param title: Title of the feedback
    :return:
    """

    feedback = f'#{title}'
    feedback += '\n'
    feedback += markdown_out(testresults['feedback'])
    feedback += '\n'
    feedback += f'**{testresults["points"]:.2f}/{testresults["max"]:.2f} Punkten ({(testresults["points"]/testresults["max"])*100:.2f}%)**'
    feedback += '\n***\n'

    return feedback


def markdown_out(results: dict) -> str:
    """
    creates a Markdown table from the results
    :param results:
    :return:
    """
    # if results is empty return string
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
    if DEBUG: print('######### UPLOAD TO MOODLE ######### ')
    if DEBUG: print(url)
    if DEBUG: print(payload)
    response = requests.post(url=url, data=payload, timeout=30)
    if DEBUG: print(response)
    if DEBUG: print(response.text)


if __name__ == '__main__':
    from dotenv import load_dotenv

    # loading variables from .env file
    load_dotenv()
    main()
