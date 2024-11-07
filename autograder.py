""" Main script for grading assignments """

from classroom_notifier import notify_classroom
from moodle_notifier import update_moodle  # Now we call update_moodle with test_result_collection
from pylint_runner import run_pylint
from pytest_runner import run_pytest

DEBUG = False


def main():
    print ('#### TESTING ###')
    # Collect results
    test_result_collection = collect_results()

    # Update Moodle and notify classroom using the test_result_collection
    update_moodle(test_result_collection)
    notify_classroom(test_result_collection)


def collect_results() -> list:
    test_result_collection = []

    for func, title in [(run_pytest, 'Unittests'), (run_pylint, 'Linting')]:
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
