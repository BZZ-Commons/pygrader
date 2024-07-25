import os
import json
import shutil
import tkinter as tk
from tkinter import filedialog


def select_project_folder():
    """Open a dialog to select the project folder."""
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    folder_selected = filedialog.askdirectory()
    return folder_selected


def read_json(file_path):
    """Read JSON file and return its content."""
    with open(file_path, 'r') as file:
        return json.load(file)


def write_json(file_path, content):
    """Write content to a JSON file."""
    with open(file_path, 'w') as file:
        json.dump(content, file, indent=2)


def convert_autograding(json_content):
    """Convert autograding.json format to unittests.json format."""
    tests = json_content['tests']
    new_tests = [{'name': test['name'], 'function': test['name'], 'timeout': test['timeout'], 'points': test['points']}
                 for test in tests]
    return new_tests


def list_root_python_files(folder_path):
    """List all Python files in the root folder that do not contain pytest."""
    python_files = []
    for file in os.listdir(folder_path):
        if file.endswith('.py') and 'test_' not in file and '_test' not in file:
            python_files.append(file)
    return python_files


def main():
    # Select the project folder
    project_folder = select_project_folder()

    if not project_folder:
        print('No folder selected. Exiting...')
        return

    # Paths
    github_folder = os.path.join(project_folder, '.github')
    classroom_folder = os.path.join(github_folder, 'classroom')
    autograding_folder = os.path.join(github_folder, 'autograding')

    autograding_json_path = os.path.join(classroom_folder, 'autograding.json')
    unittests_json_path = os.path.join(autograding_folder, 'unittests.json')
    lint_json_path = os.path.join(autograding_folder, 'lint.json')
    pylintrc_path = os.path.join(os.getcwd(), 'templates_for_repo_converter/pylintrc')
    dest_pylintrc_path = os.path.join(autograding_folder, 'pylintrc')

    workflows_folder = os.path.join(github_folder, 'workflows')
    classroom_yml_path = os.path.join(os.getcwd(), 'templates_for_repo_converter/classroom.yml')
    dest_classroom_yml_path = os.path.join(workflows_folder, 'classroom.yml')
    copyissues_yml_path = os.path.join(os.getcwd(), 'templates_for_repo_converter/copyissues.yml')
    dest_copyissues_yml_path = os.path.join(workflows_folder, 'copyissues.yml')

    # Create necessary folders
    os.makedirs(autograding_folder, exist_ok=True)
    os.makedirs(workflows_folder, exist_ok=True)

    # Convert autograding.json to unittests.json
    autograding_content = read_json(autograding_json_path)
    unittests_content = convert_autograding(autograding_content)
    write_json(unittests_json_path, unittests_content)

    # Create lint.json
    python_files = list_root_python_files(project_folder)
    lint_content = {'files': python_files, 'ignore': [], 'max': 20}
    write_json(lint_json_path, lint_content)

    # Copy pylintrc
    if os.path.exists(pylintrc_path):
        shutil.copy(pylintrc_path, dest_pylintrc_path)

    # Copy classroom.yml and copyissues.yml
    if os.path.exists(classroom_yml_path):
        shutil.copy(classroom_yml_path, dest_classroom_yml_path)
    if os.path.exists(copyissues_yml_path):
        shutil.copy(copyissues_yml_path, dest_copyissues_yml_path)

    # Remove classroom folder
    if os.path.exists(classroom_folder):
        shutil.rmtree(classroom_folder)

    print('Operation completed successfully.')


if __name__ == '__main__':
    main()
