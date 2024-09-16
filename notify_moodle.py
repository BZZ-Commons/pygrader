import urllib.parse
import xml.etree.ElementTree as ET
import sys
import requests
import os
from utils import bcolors

DEBUG = True


def update_moodle(test_result_collection: list):
    """
    Update Moodle with the test results, similar interface to notify_classroom.

    Args:
        test_result_collection (list): A list containing results from tests and linting.
    """
    # Assuming the environment variables are already set, similar to the original implementation.
    env_vars = {
        'target_url': os.environ['TARGET_URL'],
        'token': os.getenv('TOKEN'),
        'function': os.environ['FUNCTION'],
        'username': os.environ['USERNAME'],
        'server': os.environ['SERVER'],
        'repo_path': os.environ['REPO'],
    }

    repository = env_vars['repo_path'].split('/')[1]
    assignment = repository.split('-' + env_vars['username'])[0]

    # Combine the results into a single summary
    result = {
        'points': 0.0,
        'max': 0.0,
        'feedback': ''
    }

    # Iterate over the test result collection to aggregate points, max, and feedback
    for test_result in test_result_collection:
        result['points'] += test_result['points']
        result['max'] += test_result['max']
        result['feedback'] += wrap_feedback_table(test_result)

    result['points'] = round(result['points'], 2)

    # Construct the external link to the repo
    external_link = f'{env_vars["server"]}/{env_vars["repo_path"]}'

    # Call Moodle API to submit the result
    url = f'{env_vars["target_url"]}/webservice/rest/server.php/?wstoken={env_vars["token"]}&wsfunction={env_vars["function"]}'
    feedback = urllib.parse.quote(result['feedback'])
    payload = {
        'assignment_name': assignment,
        'user_name': env_vars['username'],
        'points': result['points'],
        'max': result['max'],
        'externallink': external_link,
        'feedback': feedback
    }

    print_moodle_payload(payload)

    if DEBUG:
        print(url)
        print(payload)

    # Send the request to Moodle
    response = requests.post(url=url, data=payload, timeout=30)

    if DEBUG:
        print(response)
        print(response.text)

    # Parse the response from Moodle
    parse_moodle_response(response.text)


def wrap_feedback_table(test_result: dict) -> str:
    """
    Generate markdown feedback for each test result in a table format.

    Args:
        test_result (dict): A dictionary containing 'feedback', 'points', and 'max' for a test.

    Returns:
        str: Formatted markdown feedback string.
    """
    feedback = f'## {test_result["name"]}\n'

    # Generate the markdown table
    if test_result['feedback']:
        headers = test_result['feedback'][0].keys()
        table = '| ' + ' | '.join(headers) + ' |\n'
        table += '| ' + ' | '.join(['---'] * len(headers)) + ' |\n'
        for entry in test_result['feedback']:
            table += '| ' + ' | '.join(str(entry[h]) for h in headers) + ' |\n'
        feedback += table

    # Add the summary points
    feedback += f'\n**{test_result["points"]:.2f}/{test_result["max"]:.2f} Points ({(test_result["points"] / test_result["max"]) * 100:.2f}%)**\n\n'
    feedback += '---\n'
    return feedback


def parse_moodle_response(response_text: str) -> None:
    """
    Parse the Moodle API response and handle success or failure.
    """
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
    """
    Handle any error returned by Moodle during the update process.
    """
    message_key = root.find(".//KEY[@name='message']/VALUE")
    if message_key is not None:
        print(f"{bcolors.FAIL}❌ Upload to Moodle failed.{bcolors.ENDC}")
        formatted_message = message_key.text.replace('\\n', '\n')
        print(f"{bcolors.FAIL}❌ Error message: {formatted_message}{bcolors.ENDC}")
    else:
        message_key = root.find(".//MESSAGE")
        if message_key is not None:
            print(f"{bcolors.FAIL}❌ Upload to Moodle failed.{bcolors.ENDC}")
            print(f"{bcolors.FAIL}❌ Error message: {message_key.text}{bcolors.ENDC}")
        else:
            print(f"{bcolors.FAIL}❌ Upload to Moodle failed.{bcolors.ENDC}")
            print(f"{bcolors.FAIL}❌ No error message found. See log:{bcolors.ENDC}")
            print(f'{bcolors.FAIL}{ET.tostring(root, encoding="unicode")}{bcolors.ENDC}')


def print_moodle_payload(payload: dict) -> None:
    """
    Print the payload that will be sent to Moodle for updating the assignment.
    """
    print('\n\n')
    print(f'{bcolors.HEADER}################################################################################{bcolors.ENDC}')
    print(f'{bcolors.HEADER}{bcolors.BOLD}UPLOAD TO MOODLE{bcolors.ENDC}')
    print(f'{bcolors.HEADER}################################################################################{bcolors.ENDC}')
    print(f'{bcolors.OKCYAN}{bcolors.BOLD}🏆 Total Points: \t{payload["points"]}/{payload["max"]}{bcolors.ENDC}')
    print(f'{bcolors.OKCYAN}👤 User : \t\t{payload["user_name"]}{bcolors.ENDC}')
    print(f'{bcolors.OKCYAN}📝 Assignment : \t{payload["assignment_name"]}{bcolors.ENDC}')
    print(f'{bcolors.OKCYAN}🔗 Link : \t\t{payload["externallink"]}{bcolors.ENDC}')
