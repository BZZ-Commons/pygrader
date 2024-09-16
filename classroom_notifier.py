import json
import os
import subprocess

from utils import bcolors


def notify_classroom(results):
    """
    Combine max score and total score from each runner's results, and update the check run.

    Args:
        results (list): List of dicts, each containing runner results with 'max' and 'points'.
    """
    # Combine max score and total score
    max_points = float(sum(result.get('max', 0) for result in results))
    total_points = float(sum(result.get('points', 0) for result in results))

    if max_points == 0:
        print(f"{bcolors.FAIL}❌ Max points are zero, exiting...{bcolors.ENDC}")
        return

    # Get GitHub token and repository details from environment variables
    token = os.getenv('GH_TOKEN')
    if not token:
        print(f"{bcolors.FAIL}❌ GITHUB_TOKEN is missing{bcolors.ENDC}")
        return

    nwo = os.getenv('GITHUB_REPOSITORY', '/')
    if '/' not in nwo:
        print(f"{bcolors.FAIL}❌ Invalid GITHUB_REPOSITORY format{bcolors.ENDC}")
        return

    owner, repo = nwo.split('/')
    if not owner or not repo:
        print(f"{bcolors.FAIL}❌ Owner or repository is missing{bcolors.ENDC}")
        return

    try:
        run_id = int(os.getenv('GITHUB_RUN_ID', ''))
    except ValueError:
        print(f"{bcolors.FAIL}❌ Invalid GITHUB_RUN_ID{bcolors.ENDC}")
        return

    # Fetch the workflow run using GitHub CLI
    workflow_run_response = subprocess.run(
        ['gh', 'api', f'/repos/{owner}/{repo}/actions/runs/{run_id}'],
        capture_output=True,
        text=True
    )

    if workflow_run_response.returncode != 0:
        print(f"{bcolors.FAIL}❌ Failed to fetch workflow run: {workflow_run_response.stderr}{bcolors.ENDC}")
        return

    try:
        workflow_data = json.loads(workflow_run_response.stdout)
        check_suite_url = workflow_data.get('check_suite_url')
        check_suite_id = check_suite_url.split('/')[-1]
    except (json.JSONDecodeError, AttributeError, IndexError):
        print(f"{bcolors.FAIL}❌ Error parsing workflow run response{bcolors.ENDC}")

        return

    # List the check runs for the suite using GitHub CLI
    check_runs_response = subprocess.run(
        ['gh', 'api', f'/repos/{owner}/{repo}/check-suites/{check_suite_id}/check-runs'],
        capture_output=True,
        text=True
    )

    if check_runs_response.returncode != 0:
        print(f"{bcolors.FAIL}❌ Failed to list check runs: {check_runs_response.stderr}{bcolors.ENDC}")
        return

    try:
        check_runs_data = json.loads(check_runs_response.stdout)
        check_run_id = check_runs_data["check_runs"][0].get('id')
    except (json.JSONDecodeError, KeyError, IndexError):
        print(f"{bcolors.FAIL}❌ No matching check run found or error parsing response.{bcolors.ENDC}")
        return

    # Update the check run with the autograding results using GitHub CLI
    text = f"Points {total_points}/{max_points}"
    update_command = [
        'gh', 'api', f'/repos/{owner}/{repo}/check-runs/{check_run_id}', '--method', 'PATCH',
        '-f', 'output[title]=Autograding',
        '-f', f'output[summary]={text}',
        '-f', f'output[text]={json.dumps({"totalPoints": total_points, "maxPoints": max_points})}',
        '-F', 'output[annotations][][path]=.github',
        '-F', 'output[annotations][][start_line]=1',
        '-F', 'output[annotations][][end_line]=1',
        '-F', 'output[annotations][][annotation_level]=notice',
        '-F', f'output[annotations][][message]={text}',
        '-F', 'output[annotations][][title]=Autograding complete'
    ]

    update_response = subprocess.run(update_command, capture_output=True, text=True)
    if update_response.returncode != 0:
        print(f"{bcolors.FAIL}❌ Upload to Classroom failed.{bcolors.ENDC}")
    else:
        print(f"Check run updated: {text}")
        print(f"{bcolors.OKGREEN}✅ Upload to Classroom successful.{bcolors.ENDC}")
        return
