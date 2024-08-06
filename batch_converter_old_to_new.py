import os
import json
import shutil
import subprocess
from dotenv import load_dotenv


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
    """List all Python files in the root folder that do not contain pytest or xxx_test."""
    python_files = []
    for file in os.listdir(folder_path):
        if file.endswith('.py') and 'test_' not in file and '_test' not in file:
            python_files.append(file)
    return python_files


def clone_repo(org_name, repo_name, github_token):
    """Clone the GitHub repository using the provided organization name and repository name."""
    repo_url = f"https://{github_token}@github.com/{org_name}/{repo_name}.git"
    subprocess.run(["git", "clone", repo_url])


def checkout_branch(branch_name):
    """Checkout the specified branch."""
    subprocess.run(["git", "checkout", branch_name])


def commit_and_push_changes(branch_name):
    """Commit the changes and push to the specified branch."""
    subprocess.run(["git", "add", "."])
    subprocess.run(["git", "commit", "-m", f"Update files for {branch_name} branch"])
    subprocess.run(["git", "push", "origin", branch_name])


def process_repository(org_name, repo_name, github_token, template_dir):
    """Process a single repository by cloning, making changes, and pushing updates."""
    # Clone the repository
    clone_repo(org_name, repo_name, github_token)

    # Change directory to the cloned repository
    os.chdir(repo_name)

    # Branches to update
    branches = ['main', 'solution']

    for branch in branches:
        # Checkout the branch
        checkout_branch(branch)

        # Paths
        project_folder = os.getcwd()
        github_folder = os.path.join(project_folder, '.github')
        classroom_folder = os.path.join(github_folder, 'classroom')
        autograding_folder = os.path.join(github_folder, 'autograding')

        autograding_json_path = os.path.join(classroom_folder, 'autograding.json')
        unittests_json_path = os.path.join(autograding_folder, 'unittests.json')
        lint_json_path = os.path.join(autograding_folder, 'lint.json')
        pylintrc_path = os.path.join(template_dir, 'pylintrc')
        dest_pylintrc_path = os.path.join(autograding_folder, 'pylintrc')

        workflows_folder = os.path.join(github_folder, 'workflows')
        classroom_yml_path = os.path.join(template_dir, 'classroom.yml')
        dest_classroom_yml_path = os.path.join(workflows_folder, 'classroom.yml')
        copyissues_yml_path = os.path.join(template_dir, 'copyissues.yml')
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
        lint_content = {'files': python_files, 'ignore': [], 'max': 5}
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

        # Commit and push the changes to the current branch
        commit_and_push_changes(branch)

    # Go back to the parent directory before processing the next repository
    os.chdir('..')

    # Optionally, remove the cloned repository folder after processing
    shutil.rmtree(repo_name)


def main():
    # Capture the original working directory
    original_working_dir = os.getcwd()

    # Directory containing the templates
    template_dir = os.path.join(original_working_dir, 'templates_for_repo_converter')

    # GitHub organization name
    org_name = "BZZ-M323"

    # List of repositories to process
    repo_names = [
        "m323-lu01-a03-funktionaler-bubblesort",
        "m323-lu01-a04-funktionaler-ggt",
        "m323-lu01-a05-sum",
        "m323-lu02-a01-pure1",
        "m323-lu02-a02-pure2",
        "m323-lu02-a03-pure3",
        "m323-lu02-a04-immutable1",
        "m323-lu02-a05-immutable2",
        "m323-lu02-a06-immutable3",
        "m323-lu02-a07-buchhaltung",
        "m323-lu02-a08-kochbuch",
        "m323-lu03-a01-verzeichnisbaum",
        "m323-lu03-a03-taskscheduler",
        "m323-lu03-a04-filter",
        "m323-lu03-a05-lager",
        "m323-lu03-a06-transformation",
        "m323-lu03-a02-zinseszins",
        "m323-lu03-a07-abschreibung",
        "m323-lu04-a12-sorting",
        "m323-lu03-a08-countries",
        "m323-lu03-a10-timer",
        "m323-lu03-a09-callback",
        "m323-lu04-a01-lambda",
        "m323-lu04-a02-lambda",
        "m323-lu04-a03-comprehensions",
        "m323-lu04-a04-comprehensions",
        "m323-lu04-a05-map",
        "m323-lu04-a06-map",
        "m323-lu04-a07-filter",
        "m323-lu04-a08-filter",
        "m323-lu04-a09-reduce",
        "m323-lu04-a10-reduce",
        "m323-lu04-a13-ternary",
        "m323-lu04-a14-ternary",
        "m323-lu04-a11-sorting",
        "m323-lu06-a01-routing",
        "m323-lu06-a02-routingjson",
        "m323-lu04-a15-generator",
        "m323-lu04-a16-generator",
        "m323-lu04-a17-generatorexpression",
        "m323-lu05-a01-args",
        "m323-lu05-a02-args2",
        "m323-lu05-a03-args3",
        "m323-lu05-a04-kwargs",
        "m323-lu05-a05-kwargs2",
        "m323-lu05-a06-inner",
        "m323-lu05-a07-inner2",
        "m323-lu04-a18-slicing",
        "m323-lu05-a08-closures",
        "m323-lu05-a10-decorator",
        "m323-lu05-a11-decorator2",
        "m323-lu05-a09-closures2",
        "m323-lu06-a03-dao",
        "m323-lu06-a04-restful",
        "m323-lu06-a05-authentication",
        "m323-lu06-a06-blueprints",
        "m323-lu06-a07-multiuser",
        "m323-lu06-a08-hashing",
        # Add other repository names here
    ]

    # GitHub access token
    github_token = os.environ['GITHUB_TOKEN']

    # Process each repository
    for repo_name in repo_names:
        process_repository(org_name, repo_name, github_token, template_dir)

    print('Operation completed successfully for all repositories.')


if __name__ == '__main__':
    load_dotenv()
    main()
