import requests
from dotenv import load_dotenv
import os

def get_repos(org_name, keyword):
    """
    Fetches a list of repositories from a GitHub organization that match a specific keyword.

    Parameters:
    org_name (str): The name of the GitHub organization.
    keyword (str): The keyword to filter repositories.

    Returns:
    list: A list of repository names that match the keyword.
    """
    url = f'https://api.github.com/orgs/{org_name}/repos'
    github_token = os.environ['GITHUB_TOKEN']

    headers = {
        'Authorization': f'token {github_token}'
    }
    repos = []
    params = {
        'per_page': 100
    }

    while url:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            data = response.json()
            filtered_repos = [repo['name'] for repo in data if keyword in repo['name']]
            repos.extend(filtered_repos)
            url = response.links.get('next', {}).get('url')
        else:
            print(f'Failed to fetch repositories: {response.status_code}')
            break

    return repos


if __name__ == '__main__':
    load_dotenv()
    org_name = 'BZZ-M323'
    keyword = 'm323'
    repos = get_repos(org_name, keyword)

    if repos:
        print('Found repositories:')
        for repo in repos:
            print(f"\"{repo}\",")
    else:
        print('No repositories found')