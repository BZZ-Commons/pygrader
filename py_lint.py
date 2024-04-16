from pylint import lint
from pylint.reporters import CollectingReporter


def py_lint():
    pylint_opts = [
        'main.py',
    ]

    reporter = CollectingReporter()
    pylint_obj = lint.Run(pylint_opts, reporter=reporter, exit=False)
    results = {
        'category': 'pylint',
        'points': 0,
        'max': 10,
        'feedback': []
    }
    for message in reporter.messages:
        output = {
            'category': message.category,
            'message': message.msg,
            'path': message.path,
            'line': message.line
        }
        results['feedback'].append(output)

    results['points'] = pylint_obj.linter.stats.global_note

    #print(results)
    return results


if __name__ == '__main__':
    pass
