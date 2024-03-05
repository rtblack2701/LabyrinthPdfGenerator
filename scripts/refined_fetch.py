import requests
import json
from jotform_api.configuration.config_loader import load_encrypted_config
from jotform import JotformAPIClient
from datetime import datetime
import os

# Assume the functions load_encrypted_config, save_image_from_url already exist

def extract_participant_data(submission):
    """
    Extract and transform participant data from a single submission.
    """
    # Helper function to extract a value by name
    def extract_value_by_name(name_key, answers):
        for answer in answers.values():
            if answer.get('name') == name_key:
                return answer.get('answer', '')
        return ''

    # Transform common fields
    common_fields = {
        "submission_id": submission['id'],
        "created_at": submission['created_at'],
        "start_date": extract_value_by_name('start_date', submission['answers']),
        "email": extract_value_by_name('email', submission['answers']),
        "contact_name": extract_value_by_name('contact_name', submission['answers']),
        "convicted_details": extract_value_by_name('convicted_details', submission['answers']),
        "source": extract_value_by_name('source', submission['answers']),
        "address": extract_value_by_name('address', submission['answers']),
        "postcode": extract_value_by_name('postcode', submission['answers']),
        "phone": extract_value_by_name('phone', submission['answers']),
        "relationship": extract_value_by_name('relationship', submission['answers']),
        "emergency_contact_phone": extract_value_by_name('emergency_contact_phone', submission['answers']),
        "mobile": extract_value_by_name('mobile', submission['answers']),
        "consent": extract_value_by_name('consent', submission['answers']),
        "convicted": extract_value_by_name('convicted', submission['answers']),
        "signed": extract_value_by_name('signed', submission['answers']),
        # Temporarily commenting out image handling for efficiency
        # "signature_image_path": download_and_save_signature_image(submission['answers']['signed']),
        "participants": []  # Placeholder for participant details
    }

    # Process participants
    for i in range(1, 4):  # Assuming up to 3 participants
        participant_prefix = f'p{i}_'
        participant = {}
        for key, value in submission['answers'].items():
            if key.startswith(participant_prefix):
                clean_key = key[len(participant_prefix):]
                participant[clean_key] = value.get('answer', '')
        
        # Add participant if there are details present
        if participant:
            common_fields['participants'].append(participant)
    
    return common_fields


def clean_data(data):
    """
    Apply cleaning logic directly to the in-memory data.
    """
    # Initialize lists and variables for processing
    cleaned_data = []
    completed_ids = set() # This should be a set or list of completed submission IDs
    exceptions = {'email', 'signed', 'signature_image_path'}
    date_fields = {'created_at', 'start_date', 'participant.dob'}

    # Assuming completed_ids are known or fetched from another source

    for submission in data:
        # Remove completed submissions
        if submission['submission_id'] not in completed_ids:
            # Consolidate participants
            participants = []
            participant_keys = [key for key in submission.keys() if key.startswith('p') and '_' in key]
            unique_ids = sorted(set(key.split('_')[0] for key in participant_keys))
            
            for uid in unique_ids:
                participant_data = {key.split('_', 1)[1]: submission.pop(key) for key in participant_keys if key.startswith(uid)}
                if participant_data:
                    participants.append(participant_data)
            
            if participants:
                submission['participant'] = participants
            
            # Apply uppercase transformation except for exceptions
            def process_entry(entry, parent_key=''):
                for key, value in entry.items():
                    full_key = f"{parent_key}.{key}" if parent_key else key
                    
                    if isinstance(value, str) and full_key not in exceptions:
                        entry[key] = value.upper()
                    elif isinstance(value, dict):
                        process_entry(value, full_key)
                    elif isinstance(value, list):
                        for item in value:
                            if isinstance(item, dict):
                                process_entry(item, full_key)
            
            process_entry(submission)
            
            def format_date_fields(submission, date_fields):
                def process_entry(entry, path_list):
                    if not path_list:  # Base case: no more path segments to process
                        return
                    current_path, *remaining_paths = path_list
                    if isinstance(entry, dict) and current_path in entry:
                        if remaining_paths:  # If there are more paths, recurse deeper
                            process_entry(entry[current_path], remaining_paths)
                        else:  # If this is the target field, attempt to format the date
                            value = entry[current_path]
                            if isinstance(value, str):  # Ensure the value is a string
                                try:
                                    parsed_date = datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
                                    entry[current_path] = parsed_date.strftime("%d/%m/%Y")
                                except ValueError:
                                    pass

                for field in date_fields:
                    path_list = field.split('.')
                    process_entry(submission, path_list)

            # Example usage
            date_fields = ['created_at', 'start_date', 'participants.dob']
            for submission in cleaned_data:
                format_date_fields(submission, date_fields)
            
            cleaned_data.append(submission)
    
    return cleaned_data

def fetch_and_process_data(api_key, form_id):
    """
    Fetches data and processes it in-memory, combining transformation and cleaning.
    """
    url = f'https://eu-api.jotform.com/form/{form_id}/submissions'
    params = {'apiKey': api_key}
    response = requests.get(url, params=params)

    if response.status_code != 200:
        raise Exception(f"Request failed with status code: {response.status_code}")

    data = response.json()
    processed_data = []

    for submission in data.get('content', []):
        if submission['status'] == 'ACTIVE':
            transformed_submission = extract_participant_data(submission)
            cleaned_submission = clean_data([transformed_submission])
            processed_data.append(cleaned_submission)

    return processed_data

def write_final_output(data, file_path='final_output.json'):
    """
    Writes the processed data to a file or another output form.
    """
    with open(file_path, 'w') as json_file:
        json.dump(data, json_file, indent=4)
    print(f"Data has been written to {file_path}")

# Main execution
try:
    key_path = "jotform_api/configuration/encryption_key.key"
    config_path = "jotform_api/configuration/encrypted_config_file.enc"
    config = load_encrypted_config(key_path, config_path)
    api_key = config.get("JOTFORM_API_KEY")
    form_id = config.get("JOTFORM_LTJJC_INDUCTION_FORM_ID")

    processed_data = fetch_and_process_data(api_key, form_id)
    write_final_output(processed_data)
except Exception as e:
    print(f"Error: {e}")
