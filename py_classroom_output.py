import json

def generate_feedback_for_classroom(input_data):
    output = transform_feedback(input_data)
    print("AAAAAAAAA")
    print(json.dumps(output, indent=2))


def transform_feedback(input_data):
    """
    Transforms the input test and linter result data into a new structured format.

    Args:
        input_data (list): A list containing feedback dictionaries from both tests and linter.

    Returns:
        dict: Transformed data in the required format.
    """

    transformed_data = {
        'version': 3,
        'status': 'pass',  # Default to pass; will be set to fail if any test fails
        'tests': [],
        'max_score': 0  # Will be updated as we process the data
    }

    total_points = 0
    total_max = 0
    task_id_counter = 0

    for data in input_data:
        if data['category'] == 'pytest':
            for test in data['feedback']:
                test_entry = {
                    'name': test['name'].replace('_', ' '),
                    'status': 'pass' if test['feedback'] == 'Success' else 'fail',
                    'message': '',  # Placeholder message
                    'test_code': '',  # Empty as per the requirement
                    'task_id': task_id_counter,
                    'filename': '',  # Empty as per the requirement
                    'line_no': 0,  # Line number set to 0
                    'duration': 0,  # Duration set to 0
                    'score': test['points']  # Points taken from the JSON
                }

                # If the test failed, we add a failure message
                if test_entry['status'] == 'fail':
                    test_entry['message'] = (
                        f"assert {test['actual']} == {test['expected']}\n  comparison failed\n"
                        f"  Obtained: {test['actual']}\n  Expected: {test['expected']}"
                    )
                    transformed_data['status'] = 'fail'  # Set overall status to fail if any test fails

                transformed_data['tests'].append(test_entry)
                task_id_counter += 1

            # Sum up points and max for pytest
            total_points += data['points']
            total_max += data['max']

        elif data['category'] == 'pylint':
            linter_points = data['points']
            linter_max = data['max']

            # Linting feedback entry
            for lint in data['feedback']:
                linter_entry = {
                    'name': 'Linting feedback',
                    'status': 'fail' if linter_points < linter_max else 'pass',
                    'message': f"{lint['category'].capitalize()} at {lint['path']}:{lint['line']} - {lint['message']}",
                    'test_code': '',  # Empty as per the requirement
                    'task_id': task_id_counter,
                    'filename': lint['path'],
                    'line_no': lint['line'],
                    'duration': 0,  # No duration for linting
                    'score': linter_points
                }

                if linter_entry['status'] == 'fail':
                    transformed_data['status'] = 'fail'  # Set overall status to fail if any lint feedback fails

                transformed_data['tests'].append(linter_entry)
                task_id_counter += 1

            total_points += linter_points
            total_max += linter_max

    # Set max_score as the sum of max points from both linter and tests
    transformed_data['max_score'] = total_max

    return transformed_data


def main():
    # Example usage:
    input_data = [
        {
            'category': 'pytest',
            'points': 4,
            'max': 9,
            'feedback': [
                {'name': 'test_in_meters_per_second', 'feedback': 'Success', 'expected': '', 'actual': '', 'points': 1,
                 'max': 1},
                {'name': 'test_reaction_distance', 'feedback': 'Success', 'expected': '', 'actual': '', 'points': 1,
                 'max': 1},
                {'name': 'test_braking_distance_dry', 'feedback': 'Assertion Error', 'expected': '28.57 ± 2.9e-01',
                 'actual': '2.857142857142857', 'points': 0, 'max': 1}
            ]
        },
        {
            'category': 'pylint',
            'points': 8.42,
            'max': 10,
            'feedback': [
                {'category': 'convention', 'message': 'C0301 Line too long (131/120)', 'path': 'main.py', 'line': 32},
                {'category': 'warning', 'message': "W0612 Unused variable 'inner_func'", 'path': 'main.py', 'line': 64},
                {'category': 'warning', 'message': 'W0101 Unreachable code', 'path': 'main.py', 'line': 70}
            ]
        }
    ]

    transformed_output = transform_feedback(input_data)
    print(transformed_output)
    return

if __name__ == '__main__':
    main()