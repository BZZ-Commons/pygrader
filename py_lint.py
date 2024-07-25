""" This script is used to lint Python files using pylint. It uses the configuration file
    .github/autograding/pylint.json to specify the files to be linted and the maximum points.
    The script returns a dictionary with the following keys
    - category: The category of the test
    - points: The points obtained
    - max: The maximum points
    - feedback: A list of feedback messages
    Each feedback message is a dictionary with the following keys
    - category: The category of the message
    - message: The message
    - path: The path to the file
    - line: The line number
    The points are calculated as follows:
    - The total points are calculated by dividing the global note by 10
    - The points are scaled to the maximum points specified in the configuration file
"""

from pylint import lint
from pylint.reporters import CollectingReporter

import os
import json
import glob
import re

DEBUG = False


def py_lint():
    pylint_opts = [
        '--rcfile=.github/autograding/pylintrc',
    ]

    config = load_config()

    # If files are specified in the config, use only them
    files = config.get('files')
    if files:
        pylint_opts.extend(files)

    # Otherwise, use all Python files in the directory, except the ones specified in the ignore list
    else:
        python_files = glob.glob('*.py', recursive=True)

        ignore_patterns = config.get('ignore')
        if ignore_patterns:
            for pattern in ignore_patterns:
                regex = re.compile(pattern)
                python_files = [f for f in python_files if not regex.match(f)]

        # Ensure the list is unique
        pylint_opts.extend(list(set(python_files)))

    reporter = CollectingReporter()
    pylint_obj = lint.Run(pylint_opts, reporter=reporter, exit=False)
    results = {
        'category': 'pylint',
        'points': 0,
        'max': 10,
        'feedback': []
    }
    max_value = load_config().get('max')
    if max_value:
        results['max'] = max_value

    for message in reporter.messages:
        output = {
            'category': message.category,
            'message': message.msg,
            'path': message.path,
            'line': message.line
        }
        results['feedback'].append(output)

    # Scale the points to the max points
    results['points'] = pylint_obj.linter.stats.global_note/10 * results['max']
    if DEBUG: print(results)
    return results


def load_config() -> dict:
    file_lint = os.environ['FILE_LINT']
    try:
        with open(f'./.github/autograding/{file_lint}', encoding='UTF-8') as file:
            params = json.load(file)
    except IOError:
        print(f'file {file_lint} not found')
    return params


if __name__ == '__main__':
    py_lint()
