import json
from jotform_api.configuration.config_loader import load_encrypted_config
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
    submission_ids = []
    # Assuming the JSON structure is a list of lists of dictionaries
    for submission_list in data:  
        for submission in submission_list:
            submission_ids.append(submission['submission_id'])
    return submission_ids

processed_file_path = 'jotform_api/completed_submissions/completed_submissions.json' 
submission_ids = read_submission_ids('jotform_api/data_files/submission_data.json') 
key_path = "jotform_api/configuration/encryption_key.key"
config_path = "jotform_api/configuration/encrypted_config_file.enc"
config = load_encrypted_config(key_path, config_path)
form_id = config.get("JOTFORM_LTJJC_INDUCTION_FORM_ID")

update_processed_submissions(processed_file_path, str(form_id), submission_ids)

