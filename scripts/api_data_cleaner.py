import json
from datetime import datetime

def clean_data(input_json_file, output_json_file, completed_submissions_file):
    def read_json(file_path):
        with open(file_path, 'r') as file:
            return json.load(file)
    
    def remove_completed_submissions(data, completed_ids):
        filtered_data = []
        printed_ids = set()  # Keep track of printed submission_ids

        for submission in data:
            if submission['submission_id'] in completed_ids:
                # Only print the message if we haven't already printed this submission_id
                if submission['submission_id'] not in printed_ids:
                    print(f"Removing submission_id: {submission['submission_id']} as it has already been processed.")
                    printed_ids.add(submission['submission_id'])
            else:
                filtered_data.append(submission)
        return filtered_data

    
    def consolidate_participants(data):
        for submission in data:
            participants = []
            participant_keys = [key for key in submission.keys() if key.startswith('p') and '_' in key]
            unique_ids = sorted(set(key.split('_')[0] for key in participant_keys))
            
            for uid in unique_ids:
                participant_data = {key.split('_', 1)[1]: submission.pop(key) for key in participant_keys if key.startswith(uid)}
                if participant_data:
                    participants.append(participant_data)
            
            if participants:
                submission['participant'] = participants
        
        return data
    
    def uppercase_values_except(data, exceptions):
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
        
        for submission in data:
            process_entry(submission)
        return data
    
    def format_date_fields(data, date_fields):
        date_formats = ["%Y-%m-%d", "%Y-%m-%d %H:%M:%S"]
        
        def process_entry(entry, parent_key=''):
            for key, value in entry.items():
                full_key = f"{parent_key}.{key}" if parent_key else key
                
                if full_key in date_fields and isinstance(value, str):
                    for format in date_formats:
                        try:
                            parsed_date = datetime.strptime(value, format)
                            entry[key] = parsed_date.strftime("%d/%m/%Y")
                            break
                        except ValueError:
                            continue
        
        for submission in data:
            process_entry(submission)
        return data
    
    # Load the completed submission IDs
    completed_submissions = read_json(completed_submissions_file)
    completed_ids = completed_submissions["240582874730360"]
    
    json_data = read_json(input_json_file)
    json_data = remove_completed_submissions(json_data, completed_ids)  # Apply the removal
    consolidated_data = consolidate_participants(json_data)
    with_uppercase = uppercase_values_except(consolidated_data, {'email', 'signed', 'signature_image_path'})
    final_data = format_date_fields(with_uppercase, {'created_at', 'start_date', 'participant.dob'})

    with open(output_json_file, 'w') as file:
        json.dump(final_data, file, indent=4)

try:
    clean_data('jotform_api/data_files/built_form_submission.json', 'jotform_api/data_files/cleaned_submission_data.json', 'jotform_api/completed_submissions/completed_submissions.json')
    print("Data cleaning process completed successfully")
except Exception as e:
    print(f"Error cleaning the data: {e}")
