import os
import shutil
import subprocess
from pathlib import Path
from dotenv import load_dotenv


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
    subprocess.run(
        ["git", "commit", "-m", f"Add pylint configuration and update requirements.txt for {branch_name} branch"])
    subprocess.run(["git", "push", "origin", branch_name])


def update_requirements_file(repo_path):
    """Update the requirements.txt file to include pylint version 3.2.6."""
    requirements_path = Path(repo_path) / "requirements.txt"

    if not requirements_path.exists():
        # If the file doesn't exist, create it
        with open(requirements_path, 'w', encoding='utf-8') as req_file:
            req_file.write("pylint==3.2.6\n")
    else:
        with open(requirements_path, 'r', encoding='utf-8') as req_file:
            lines = req_file.readlines()

        # Check if pylint is already in the file
        pylint_exists = False
        for i, line in enumerate(lines):
            if "pylint" in line:
                pylint_exists = True
                # Update version if necessary
                if "pylint==" not in line or line.strip() != "pylint==3.2.6":
                    lines[i] = "pylint==3.2.6\n"
                break

        # Add pylint if not found
        if not pylint_exists:
            lines.append("pylint==3.2.6\n")

        # Write back the updated content
        with open(requirements_path, 'w', encoding='utf-8') as req_file:
            req_file.writelines(lines)


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
        repo_root = Path(os.getcwd())

        # Copy all files from the template directory to the repo
        for item in Path(template_dir).iterdir():
            if item.is_dir():
                shutil.copytree(item, repo_root / item.name, dirs_exist_ok=True)
            else:
                shutil.copy2(item, repo_root / item.name)

        # Update requirements.txt
        update_requirements_file(repo_root)

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
    template_dir = os.path.join(original_working_dir, 'templates_for_add_pylint')

    # GitHub organization name
    org_name = "m323-ix22"

    # List of repositories to process
    repo_names = [
        "m323-ix22-m323-lu01-a01-imperativer-bubblesort-m323-lu01-a01-imperativer-bubblesort",
        "m323-ix22-m323-lu01-a02-imperativer-ggt-m323-lu01-a02-imperativer-ggt",
        "m323-ix22-m323-lu01-a03-funktionaler-bubblesort-m323-lu01-a03-funktionaler-bubblesort",
        "m323-ix22-m323-lu01-a04-funktionaler-ggt-m323-lu01-a04-funktionaler-ggt",
        "m323-ix22-m323-lu01-a05-sum-m323-lu01-a05-sum",
    ]

    # Load GitHub token from .env file
    load_dotenv()
    github_token = os.environ['GITHUB_TOKEN']

    # Process each repository
    for repo_name in repo_names:
        process_repository(org_name, repo_name, github_token, template_dir)

    print('Operation completed successfully for all repositories.')


if __name__ == '__main__':
    main()
