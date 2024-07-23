from pylint import lint
from pylint.reporters import CollectingReporter

import os
import json
import glob

def py_lint():
    pylint_opts = [
        '--rcfile=.github/autograding/pylintrc',
    ]

    # Add files from config file or all python files in the directory
    files = load_config().get('files')
    if files:
        pylint_opts.extend(files)
    else:
        python_files = glob.glob('./*.py')
        pylint_opts.extend(python_files)

    print(pylint_opts)
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
    FILE_LINT = os.environ['FILE_LINT']
    try:
        with open(f'./.github/autograding/{FILE_LINT}', encoding='UTF-8') as file:
            params = json.load(file)
    except IOError as ex:
        print(f'file {FILE_LINT} not found')
    return params


if __name__ == '__main__':
    py_lint()
