import subprocess

def transfer_repos(repo_list, current_owner, new_owner):
    """
    Transfers a list of repositories from one owner to another using the GitHub CLI.

    Parameters:
    repo_list (list): List of repository names to be transferred.
    current_owner (str): Current owner of the repositories.
    new_owner (str): New owner of the repositories.

    Returns:
    None
    """
    for repo in repo_list:
        command = f'gh api repos/{current_owner}/{repo}/transfer -f new_owner={new_owner}'
        try:
            print(f'Transferring repo {repo} from {current_owner} to {new_owner}')
            subprocess.run(command, shell=True, check=True)
            print(f'Successfully transferred {repo}')
        except subprocess.CalledProcessError as e:
            print(f'Failed to transfer {repo}: {e}')

if __name__ == '__main__':
    # List of repositories to transfer
    repos_to_transfer = [
        "m323-lu06-a08-hashing",
        # Add more repositories here
    ]

    # Current owner of the repositories
    current_owner = "templates-python"

    # New owner of the repositories
    new_owner = "BZZ-M323"

    # Transfer the repositories
    transfer_repos(repos_to_transfer, current_owner, new_owner)