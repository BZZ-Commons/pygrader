from pylint import lint
from pylint.reporters import CollectingReporter

import os
import json
import glob
import re
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
    max = load_config().get('max')
    if max:
        results['max'] = max

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
    print(results)
    return results


def load_config() -> dict:
    file_lint = os.environ['FILE_LINT']
    try:
        with open(f'./.github/autograding/{file_lint}', encoding='UTF-8') as file:
            params = json.load(file)
    except IOError as ex:
        print(f'file {file_lint} not found')
    return params


if __name__ == '__main__':
    py_lint()
