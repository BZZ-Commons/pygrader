""" Main script for grading assignments"""

import os
import sys
import urllib.parse

import requests

from py_lint import py_lint
from py_test import py_test
from utils import bcolors


import xml.etree.ElementTree as ET


DEBUG = False


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
    # Add a linkt to the repository
    result['feedback'] += f'Link zum Repository: [{os.environ["REPO"]}]({os.environ["SERVER"]}/{os.environ["REPO"]})'

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
    print('\n\n')
    print(f'{bcolors.HEADER}################################################################################{bcolors.ENDC}')
    print(f'{bcolors.HEADER}{bcolors.BOLD}UPLOAD TO MOODLE{bcolors.ENDC}')
    print(f'{bcolors.HEADER}################################################################################{bcolors.ENDC}')
    print(f'{bcolors.OKCYAN}🏆 Total Points: \t{payload["points"]}/{payload["max"]}{bcolors.ENDC}')
    print(f'{bcolors.OKCYAN}👤 User : \t\t\t{payload["user_name"]}{bcolors.ENDC}')
    print(f'{bcolors.OKCYAN}📝 Assignment : \t{payload["assignment_name"]}{bcolors.ENDC}')
    print(f'{bcolors.OKCYAN}🔗 Link : \t\t\t{payload["externallink"]}{bcolors.ENDC}')





    if DEBUG: print(url)
    if DEBUG: print(payload)
    response = requests.post(url=url, data=payload, timeout=30)
    if DEBUG: print(response)
    if DEBUG: print("")
    if DEBUG: print(response.text)

    # Check if Upload was successful
    # response.text is not just XML, it may contain other content
    xml_start = response.text.find('<?xml')

    # If an XML declaration is found, parse from that point
    if xml_start != -1:
        xml_content = response.text[xml_start:]
        try:
            root = ET.fromstring(xml_content)

            # Extract the value of the 'name' key
            name_key = root.find(".//KEY[@name='name']/VALUE")

            # Check if the value of the 'name' key is 'success'
            if name_key is not None and name_key.text == 'success':
                print(f"{bcolors.OKGREEN}✅ Upload to Moodle successful.{bcolors.ENDC}")
            else:
                # Extract the message from <KEY name="message"> for Plugin errors
                message_key = root.find(".//KEY[@name='message']/VALUE")
                if message_key is not None:
                    print(f"{bcolors.FAIL}❌ Upload to Moodle failed.{bcolors.ENDC}")
                    print(f"{bcolors.FAIL}❌ Error message: {message_key.text}{bcolors.ENDC}")

                # Extract the message from <MESSAGE> for Moodle errors
                message_key = root.find(".//MESSAGE")
                if message_key is not None:
                    print(f"{bcolors.FAIL}❌ Upload to Moodle failed.{bcolors.ENDC}")
                    print(f"{bcolors.FAIL}❌ Error: {message_key.text}{bcolors.ENDC}")

                sys.exit(1)

        except ET.ParseError as e:
            print(f"Failed to parse XML: {e}")
            sys.exit(1)
    else:
        print("No valid XML found in the response.")
        sys.exit(1)




if __name__ == '__main__':
    from dotenv import load_dotenv

    # loading variables from .env file
    load_dotenv()
    main()
