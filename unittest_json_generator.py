import sys
import os
import tkinter
from io import StringIO
from tkinter import filedialog
import pytest
import json

"""
Generates the 'unittests2.json' based on the pytests and 'lint2.json' for linting.
Used for the automatic grading in GitHub Classroom.
"""

class Capturing(list):
    """
    Captures the output to stdout and stderr
    """
    def __enter__(self):
        self._stdout = sys.stdout
        sys.stdout = self._stringio = StringIO()
        return self

    def __exit__(self, *args):
        self.extend(self._stringio.getvalue().splitlines())
        del self._stringio  # free up some memory
        sys.stdout = self._stdout


def main():
    """
    Generate the files for unittests2.json and lint2.json
    :return:
    """
    root = tkinter.Tk()
    root.withdraw()

    project_folder = filedialog.askdirectory()

    # Generate unittests2.json
    generate_unittests_json(project_folder)

    # Generate lint2.json
    generate_lint_json(project_folder)


def generate_unittests_json(project_folder):
    """
    Generate unittests2.json based on pytest collection
    :param project_folder: Path to the project folder
    """
    args = f'{project_folder} --collect-only'.split(' ')
    with Capturing() as output:
        pytest.main(args)
    json_content = '[\n'
    for line in output:
        if '<Function' in line:
            line = line.lstrip()
            name = line[10:-1]
            json_content += make_testcase(name) + ',\n'
        elif '<TestCaseFunction' in line:
            line = line.lstrip()
            name = line[18:-1]
            json_content += make_testcase(name) + ',\n'
    json_content = json_content[0:-2]
    json_content += '\n]'
    autograding_folder = os.path.join(project_folder, '.github', 'autograding')
    os.makedirs(autograding_folder, exist_ok=True)
    file_path = os.path.join(autograding_folder, 'unittests2.json')
    with open(file_path, 'w') as file:
        file.write(json_content)


def generate_lint_json(project_folder):
    """
    Generate lint2.json for linting configuration
    :param project_folder: Path to the project folder
    """
    python_files = list_python_files(project_folder)
    lint_content = {
        "files": python_files,
        "ignore": [],
        "max": 20
    }
    autograding_folder = os.path.join(project_folder, '.github', 'autograding')
    os.makedirs(autograding_folder, exist_ok=True)
    file_path = os.path.join(autograding_folder, 'lint2.json')
    with open(file_path, 'w') as file:
        file.write(json.dumps(lint_content, indent=2))


def list_python_files(folder_path):
    """
    List all Python files in the root folder that do not contain pytest or are not named _run_pylint.py
    :param folder_path: Path to the folder
    :return: List of Python files
    """
    python_files = []
    for file in os.listdir(folder_path):
        if file.endswith('.py') and 'test_' not in file and '_test' not in file and file != '_run_pylint.py':
            python_files.append(file)
    return python_files


def make_testcase(name):
    """
    Make the JSON for one testcase
    :param name: Name of the test function
    :return: JSON string for the testcase
    """
    testcase = '  {\n'  \
               f'    "name": "{name}",\n' \
               f'    "function": "{name}",\n' \
               f'    "timeout": 10,\n' \
               f'    "points": 1\n' \
               f'  }}'
    return testcase


if __name__ == '__main__':
    main()
