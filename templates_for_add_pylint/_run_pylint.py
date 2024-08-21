"""
This script runs pylint on specified Python files based on a configuration file.
It respects .gitignore and additional ignore patterns provided in the config.
"""

import json
import subprocess
import re
from pathlib import Path


def load_config(config_path):
    """Loads the lint configuration from a JSON file."""
    with open(config_path, 'r', encoding='utf-8') as config_file:
        return json.load(config_file)


def get_gitignore_patterns():
    """Reads the .gitignore file and returns the patterns."""
    gitignore_path = Path('.gitignore')
    if gitignore_path.exists():
        with gitignore_path.open('r', encoding='utf-8') as gitignore_file:
            patterns = [line.strip() for line in gitignore_file if line.strip() and not line.startswith('#')]
            return [convert_gitignore_to_regex(pattern) for pattern in patterns]
    return []


def convert_gitignore_to_regex(pattern):
    """Converts a .gitignore pattern to a valid regex pattern."""
    pattern = pattern.replace('.', r'\.')
    pattern = pattern.replace('*', r'.*')
    pattern = pattern.replace('?', r'.')
    if pattern.endswith('/'):
        pattern = pattern + r'.*'
    return pattern


def get_python_files(directory):
    """Recursively gets all Python files in the given directory."""
    return [str(file) for file in Path(directory).rglob('*.py')]


def should_ignore(file, ignore_patterns, gitignore_patterns):
    """Determines if a file should be ignored based on ignore patterns and .gitignore."""
    for pattern in ignore_patterns + gitignore_patterns:
        if re.match(pattern, file):
            return True
    return False


def run_pylint(files, pylint_config):
    """Runs pylint on the provided files with the specified configuration."""
    command = ['pylint', '--rcfile', pylint_config] + files
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        # Print the pylint output even if it fails
        print(e.stdout)
        print(e.stderr)


def main():
    config_path = '.github/autograding/lint.json'
    pylint_config_path = '.github/autograding/pylintrc'

    # Load lint configuration
    config = load_config(config_path)

    # Load .gitignore patterns
    gitignore_patterns = get_gitignore_patterns()

    # Get files to lint
    if config['files']:
        files_to_lint = [file for file in config['files'] if
                         not should_ignore(file, config['ignore'], gitignore_patterns)]
    else:
        all_files = get_python_files('.')
        files_to_lint = [file for file in all_files if not should_ignore(file, config['ignore'], gitignore_patterns)]

    # Limit the number of files if 'max' is set
    if config['max'] > 0:
        files_to_lint = files_to_lint[:config['max']]

    if not files_to_lint:
        print('No files to lint.')
        return

    # Run pylint
    run_pylint(files_to_lint, pylint_config_path)


if __name__ == '__main__':
    main()
