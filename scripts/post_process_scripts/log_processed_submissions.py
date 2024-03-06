import json

# Note list of processed submissions for each form in jotform_api/completed_submissions/completed_submissions.json
def update_processed_submissions(processed_file_path, form_id, submission_ids):
    try:
        with open(processed_file_path, 'r') as file:
            processed_submissions = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        processed_submissions = {}

    # Ensure no duplicates for form_id
    if form_id not in processed_submissions:
        processed_submissions[form_id] = []

    # Update without duplicates for submission_ids
    updated_ids = set(processed_submissions[form_id] + submission_ids)
    processed_submissions[form_id] = list(updated_ids)

    # Write back to the file
    with open(processed_file_path, 'w') as file:
        json.dump(processed_submissions, file, indent=4)


def read_submission_ids(cleaned_data_file):
    with open(cleaned_data_file, 'r') as file:
        data = json.load(file)
    submission_ids = [item['submission_id'] for item in data]  # Adjust if necessary
    return submission_ids

processed_file_path = 'jotform_api/completed_submissions/completed_submissions.json'  # Update with the actual path
submission_ids = read_submission_ids('jotform_api/data_files/cleaned_submission_data.json') # Update with the actual path
form_id = 240652651606353

update_processed_submissions(processed_file_path, str(form_id), submission_ids)

