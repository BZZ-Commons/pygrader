import json
import os
import subprocess


def notify_classroom(runner_results):
    """
    Combine max score and total score from each runner's results, and update the check run.

    Args:
        runner_results (list): List of dicts, each containing runner results.
    """
    # Combine max score and total score from each {runner, results} pair
    total_points = 0
    max_points = 0

    for runner in runner_results:
        results = runner.get('results', {})
        if 'max_score' not in results:
            continue

        max_points += results['max_score']
        for test in results.get('tests', []):
            total_points += test.get('score', 0)

    if max_points == 0:
        print("Max points are zero, exiting...")
        return

    # Get GitHub token and repository details from environment variables
    token = os.getenv('GH_TOKEN')
    if not token:
        print("GITHUB_TOKEN is missing")
        return

    nwo = os.getenv('GITHUB_REPOSITORY', '/')
    owner, repo = nwo.split('/')
    if not owner or not repo:
        print("Owner or repository is missing")
        return

    run_id = os.getenv('GITHUB_RUN_ID', '')
    try:
        run_id = int(run_id)
    except ValueError:
        print("Invalid GITHUB_RUN_ID")
        return

    # Fetch the workflow run using GitHub CLI
    workflow_run_response = subprocess.run(
        ['gh', 'api', f'/repos/{owner}/{repo}/actions/runs/{run_id}'],
        capture_output=True,
        text=True
    )
    if workflow_run_response.returncode != 0:
        print(f"Failed to fetch workflow run: {workflow_run_response.stderr}")
        return

    workflow_data = json.loads(workflow_run_response.stdout)
    check_suite_url = workflow_data.get('check_suite_url', '')
    check_suite_id = check_suite_url.split('/')[-1]

    # List the check runs for the suite using GitHub CLI
    check_runs_response = subprocess.run(
        ['gh', 'api', f'/repos/{owner}/{repo}/check-suites/{check_suite_id}/check-runs',
         '--jq'],#, '.check_runs[] | select(.name == "run-autograding-tests")'],
        capture_output=True,
        text=True
    )
    if check_runs_response.returncode != 0:
        print(f"Failed to list check runs: {check_runs_response.stderr}")
        return

    print(check_runs_response)
    print("AAA")
    check_runs_data = json.loads(check_runs_response.stdout)
    if len(check_runs_data) == 0:
        print("No matching check run found")
        return

    check_run_id = check_runs_data[0].get('id')

    # Update the check run with the autograding results using GitHub CLI
    text = f"Points {total_points}/{max_points}"
    update_command = [
        'gh', 'api', f'/repos/{owner}/{repo}/check-runs/{check_run_id}', '--method', 'PATCH',
        '-f', f'output[title]=Autograding',
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
        print(f"Failed to update check run: {update_response.stderr}")
    else:
        print(f"Check run updated: {text}")

# Example usage:
