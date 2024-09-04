""" Main script for grading assignments"""

import os
import sys
import urllib.parse
import xml.etree.ElementTree as ET

import requests

from py_lint import py_lint
from py_test import py_test
from utils import bcolors

DEBUG = False


def main():
    env_vars = {
        'target_url': os.environ['TARGET_URL'],
        'token': os.getenv('TOKEN'),
        'function': os.environ['FUNCTION'],
        'username': os.environ['USERNAME'],
        'server': os.environ['SERVER'],
        'repo_path': os.environ['REPO'],
    }

    if DEBUG:
        print(f'{env_vars}')

    repository = env_vars['repo_path'].split('/')[1]
    assignment = repository.removesuffix('-' + env_vars['username'])

    result = collect_results()
    update_moodle(
        result=result,
        target_url=env_vars['target_url'],
        token=env_vars['token'],
        function=env_vars['function'],
        user_name=env_vars['username'],
        assignment=assignment,
        external_link=f'{env_vars["server"]}/{env_vars["repo_path"]}'
    )


def collect_results() -> dict:
    result = {
        'points': 0.0,
        'max': 0.0,
        'feedback': ''
    }

    for func, title in [(py_test, 'Unittests'), (py_lint, 'Linting')]:
        testresults = func()
        result['points'] += testresults['points']
        result['max'] += testresults['max']
        result['feedback'] += wrap_feedback_table(testresults, title)

    result['feedback'] += f'Link zum Repository: [{os.environ["REPO"]}]({os.environ["SERVER"]}/{os.environ["REPO"]})'
    result['points'] = round(result['points'], 2)

    if DEBUG:
        print('######### FEEDBACK TABLES ######### ')
        print(result['feedback'])

    return result


def wrap_feedback_table(testresults: dict, title: str) -> str:
    feedback = f'#{title}\n{markdown_out(testresults["feedback"])}\n'
    feedback += f'**{testresults["points"]:.2f}/{testresults["max"]:.2f} Punkten ({(testresults["points"] / testresults["max"]) * 100:.2f}%)**\n***\n'
    return feedback


def markdown_out(results: list) -> str:
    if not results:
        return ''
    headers = results[0].keys()
    table = '| ' + ' | '.join(headers) + ' |\n'
    table += '| ' + ' | '.join(['---'] * len(headers)) + ' |\n'
    table += ''.join(f'| {" | ".join(str(entry[h]) for h in headers)} |\n' for entry in results)
    return table


def update_moodle(result: dict, target_url: str, token: str, function: str, user_name: str, assignment: str,
                  external_link: str) -> None:
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

    print_moodle_payload(payload)

    if DEBUG:
        print(url)
        print(payload)
    response = requests.post(url=url, data=payload, timeout=30)
    if DEBUG:
        print(response)
        print(response.text)

    parse_moodle_response(response.text)


def parse_moodle_response(response_text: str) -> None:
    xml_start = response_text.find('<?xml')

    if xml_start != -1:
        xml_content = response_text[xml_start:]
        try:
            root = ET.fromstring(xml_content)

            name_key = root.find(".//KEY[@name='name']/VALUE")
            if name_key is not None and name_key.text == 'success':
                print(f"{bcolors.OKGREEN}✅ Upload to Moodle successful.{bcolors.ENDC}")
            else:
                handle_moodle_error(root)
        except ET.ParseError as e:
            print(f"Failed to parse XML: {e}")
            sys.exit(1)
    else:
        print("No valid XML found in the response.")
        sys.exit(1)


def handle_moodle_error(root) -> None:
    message_key = root.find(".//KEY[@name='message']/VALUE")
    if message_key is not None:  # Message from the plugin
        # Replace \n with actual new lines for better readability
        print(f"{bcolors.FAIL}❌ Upload to Moodle failed.{bcolors.ENDC}")
        formatted_message = message_key.text.replace('\\n', '\n')
        print(f"{bcolors.FAIL}❌ Error message: {formatted_message}{bcolors.ENDC}")
    else:  # Message from Moodle
        message_key = root.find(".//MESSAGE")
        if message_key is not None:
            print(f"{bcolors.FAIL}❌ Upload to Moodle failed.{bcolors.ENDC}")
            print(f"{bcolors.FAIL}❌ Error message: {message_key.text}{bcolors.ENDC}")
        else:
            print(f"{bcolors.FAIL}❌ Upload to Moodle failed.{bcolors.ENDC}")
            print(f"{bcolors.FAIL}❌ No error message found. See log:{bcolors.ENDC}")
            print(f'{bcolors.FAIL}{ET.tostring(root, encoding="unicode")}{bcolors.ENDC}')

    sys.exit(1)


def print_moodle_payload(payload: dict) -> None:
    print('\n\n')
    print(
        f'{bcolors.HEADER}################################################################################{bcolors.ENDC}')
    print(f'{bcolors.HEADER}{bcolors.BOLD}UPLOAD TO MOODLE{bcolors.ENDC}')
    print(
        f'{bcolors.HEADER}################################################################################{bcolors.ENDC}')
    print(f'{bcolors.OKCYAN}{bcolors.BOLD}🏆 Total Points: \t{payload["points"]}/{payload["max"]}{bcolors.ENDC}')
    print(f'{bcolors.OKCYAN}👤 User : \t\t{payload["user_name"]}{bcolors.ENDC}')
    print(f'{bcolors.OKCYAN}📝 Assignment : \t{payload["assignment_name"]}{bcolors.ENDC}')
    print(f'{bcolors.OKCYAN}🔗 Link : \t\t{payload["externallink"]}{bcolors.ENDC}')


if __name__ == '__main__':
    from dotenv import load_dotenv

    # loading variables from .env file
    load_dotenv()
    main()
