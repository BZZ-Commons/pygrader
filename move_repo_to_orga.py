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
        "m323-lu01-a02-imperativer-ggt",
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

        # Add more repositories here
    ]

    # Current owner of the repositories
    current_owner = "BZZ-M323"

    # New owner of the repositories
    new_owner = "templates-python"

    # Transfer the repositories
    transfer_repos(repos_to_transfer, current_owner, new_owner)