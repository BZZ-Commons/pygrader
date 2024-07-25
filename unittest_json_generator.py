import sys
import os
import tkinter
from io import StringIO
from tkinter import filedialog
import pytest

"""
Generates the 'unittests2.json' based on the pytests.
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
    Generate the file
    :return:
    """
    root = tkinter.Tk()
    root.withdraw()

    project_folder = filedialog.askdirectory()
    args = f'{project_folder} --collect-only'.split(' ')
    with Capturing() as output:
        pytest.main(args)
    print(output)
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