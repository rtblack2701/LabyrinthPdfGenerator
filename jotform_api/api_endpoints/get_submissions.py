import requests
import json
from jotform_api.configuration.config_loader import load_encrypted_config
from jotform import JotformAPIClient
from datetime import datetime
import os

# Assume the functions load_encrypted_config, save_image_from_url already exist

def format_address_fields(common_fields):
    """Format the address and postcode fields within common_fields."""
    address_dict = common_fields.get('address', {})
    if isinstance(address_dict, dict):
        addr_line1 = address_dict.get('addr_line1', '').strip()
        city = address_dict.get('city', '').strip()
        postal = address_dict.get('postal', '').strip().upper()
        
        # Format the address string
        formatted_address = ', '.join(filter(None, [addr_line1, city]))
        common_fields['address'] = formatted_address

        # Correctly format and assign the postcode
        if len(postal) > 3:
            common_fields['postcode'] = f"{postal[:-3].rstrip()} {postal[-3:]}"
        else:
            common_fields['postcode'] = postal
    else:
        common_fields['address'] = ""
        common_fields['postcode'] = ""

# Define a directory to save the signature images
signature_images_directory = 'assets/signature_images'
if not os.path.exists(signature_images_directory):
    os.makedirs(signature_images_directory)

def save_image_from_url(url, save_path):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            with open(save_path, 'wb') as f:
                f.write(response.content)
            return True
        else:
            return False
    except Exception as e:
        return False

def extract_participant_data(submission):
    """
    Extract and transform participant data from a single submission.
    """
    # Helper function to extract a value by name
    def extract_value_by_name(name_key, answers):
        if answers is None or not isinstance(answers, dict):
            return ''
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

    signed_url = common_fields.get('signed')
    if signed_url:
        image_filename = f"{submission['id']}_signature.png"
        save_path = os.path.join(signature_images_directory, image_filename)
        if save_image_from_url(signed_url, save_path):
            # If the image is successfully saved, update the path
            common_fields['signature_image_path'] = save_path

    format_address_fields(common_fields)

    # Process participants
    for i in range(1, 4):  # Assuming up to 3 participants
        participant_data = {
            "full_name": extract_value_by_name(f'p{i}_full_name', submission['answers']),
            "dob": extract_value_by_name(f'p{i}_dob', submission['answers']),
            "medical_condition": extract_value_by_name(f'p{i}_medical_condition', submission['answers']),
            "medical_checklist": extract_value_by_name(f'p{i}_medical_checklist', submission['answers']),
            "allergy": extract_value_by_name(f'p{i}_allergy', submission['answers']),
            "other_medical": extract_value_by_name(f'p{i}_other_medical', submission['answers']),
        }

        # Check if the participant has any information filled out
        if any(participant_data.values()):
            common_fields['participants'].append(participant_data)
    
    return common_fields

def format_date(date_str):
    """Attempt to format a date string."""
    try:
        return datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y")
    except ValueError:
        return date_str  # Return the original string if formatting fails

def format_date_fields(submission):
    """Format date fields for a submission, replacing nested date structures with strings."""
    # Format 'created_at' directly
    submission['created_at'] = format_date(submission['created_at'])

    # Replace 'start_date' with formatted 'datetime' string
    if 'start_date' in submission and 'datetime' in submission['start_date']:
        submission['start_date'] = format_date(submission['start_date']['datetime'])

    # Replace each participant's 'dob' with formatted 'datetime' string
    for participant in submission.get('participants', []):
        if 'dob' in participant and 'datetime' in participant['dob']:
            participant['dob'] = format_date(participant['dob']['datetime'])


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
            
            
            format_date_fields(submission)
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

def write_submission_output(data, file_path='jotform_api/data_files/submission_data.json'):
    """
    Writes the processed data to a file or another output form.
    """
    with open(file_path, 'w') as json_file:
        json.dump(data, json_file, indent=4)
    print(f"Data has been written to {file_path}")

# Main execution
try:
    key_path = "jotform_api/configuration/clone_encryption_key.key"
    config_path = "jotform_api/configuration/clone_encrypted_config_file.enc"
    config = load_encrypted_config(key_path, config_path)
    api_key = config.get("JOTFORM_API_KEY")
    form_id = config.get("JOTFORM_LTJJC_INDUCTION_FORM_ID")

    processed_data = fetch_and_process_data(api_key, form_id)
    write_submission_output(processed_data)
except Exception as e:
    print(f"Error: {e}")
