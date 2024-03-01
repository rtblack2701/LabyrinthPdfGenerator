import pandas as pd
import json
from datetime import datetime

def clean_data(input_json_file, output_json_file):
    def read_json(file_path):
        with open(file_path, 'r') as file:
            return json.load(file)
        
    # Consolidate participant data into a list of dictionaries and remove the original participant fields e.g. p1_full_name, p1_dob, etc.
    def consolidate_participants(data):
        for submission in data:
            participants = []
            participant_keys = [key for key in submission.keys() if key.startswith('p') and '_' in key]
            unique_ids = sorted(set(key.split('_')[0] for key in participant_keys))
            
            for uid in unique_ids:
                participant_data = {key.split('_', 1)[1]: submission.pop(key) for key in participant_keys if key.startswith(uid)}
                if participant_data:  # Only add if there's actual data
                    participants.append(participant_data)
            
            if participants:
                submission['participant'] = participants
        
        return data
    
    # Make all values uppercase except for the ones in the exceptions set (email and signed fields in this case)
    def uppercase_values_except(data, exceptions):
        def process_entry(entry, parent_key=''):
            for key, value in entry.items():
                full_key = f"{parent_key}.{key}" if parent_key else key
                
                # Check if the value should be converted to uppercase
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
        """
        Convert specified date fields to DD/MM/YYYY format, handling multiple input formats.
        :param data: List of dictionaries (submissions).
        :param date_fields: List of fields to format as dates.
        """
        date_formats = ["%Y-%m-%d", "%Y-%m-%d %H:%M:%S"]  # Add more formats as needed

        def process_entry(entry, parent_key=''):
            for key, value in entry.items():
                full_key = f"{parent_key}.{key}" if parent_key else key
                
                # Attempt to format the date if the key matches and value is a string
                if full_key in date_fields and isinstance(value, str):
                    for format in date_formats:
                        try:
                            parsed_date = datetime.strptime(value, format)
                            entry[key] = parsed_date.strftime("%d/%m/%Y")
                            break  # Exit the loop on successful parsing
                        except ValueError:
                            continue  # Try the next format if parsing fails
                elif isinstance(value, dict):
                    process_entry(value, full_key)
                elif isinstance(value, list):
                    for item in value:
                        if isinstance(item, dict):
                            process_entry(item, full_key)

        for submission in data:
            process_entry(submission)
        return data
    
    
    
    exceptions = {'email', 'signed'}
    date_fields = {'created_at', 'start_date', 'participant.dob'}
    
    json_data = read_json(input_json_file)
    consolidate_participants = consolidate_participants(json_data)
    uppercase_values_except = uppercase_values_except(consolidate_participants, exceptions)
    format_date_fields = format_date_fields(uppercase_values_except, date_fields)

    with open(output_json_file, 'w') as file:
        json.dump(format_date_fields, file, indent=4)

clean_data('jotform_api/data_files/processed_submissions.json', 'jotform_api/data_files/cleaned_sub_data.json')