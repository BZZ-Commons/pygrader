""" Main script for grading assignments """

import os
from notify_classroom import notify_classroom
from notify_moodle import update_moodle  # Now we call update_moodle with test_result_collection
from pylint_runner import py_lint
from pytest_runner import py_test

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

    # Collect results
    test_result_collection = collect_results()

    # Update Moodle and notify classroom using the test_result_collection
    update_moodle(test_result_collection)
    notify_classroom(test_result_collection)


def collect_results() -> list:
    test_result_collection = []

    for func, title in [(py_test, 'Unittests'), (py_lint, 'Linting')]:
        test_results = func()
        test_results['name'] = title  # Include title for feedback generation
        test_result_collection.append(test_results)

    if DEBUG:
        print('######### FEEDBACK TABLES ######### ')
        for result in test_result_collection:
            print(result['feedback'])

    return test_result_collection


if __name__ == '__main__':
    from dotenv import load_dotenv

    # loading variables from .env file
    load_dotenv()
    main()
