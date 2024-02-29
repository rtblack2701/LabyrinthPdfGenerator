import pandas as pd
import json
from datetime import datetime

def clean_data(input_xlsx_file, output_json_file):
    def xlsx_to_json(file_path):
        df = pd.read_excel(file_path)
        return df.to_dict(orient='records')

    def convert_keys_to_snake_case(data):
        snake_case_data = []
        for entry in data:
            snake_case_entry = {}
            for key, value in entry.items():
                # Convert to snake_case and directly replace spaces with underscores
                snake_key = ''.join(['_' + c.lower() if c.isupper() else c for c in key]).lstrip('_').replace(' ', '_')
                # Remove any trailing underscores that may have been introduced
                snake_key = snake_key.rstrip('_')
                # Ensure no double underscores are present, replace them with a single underscore
                snake_key = snake_key.replace('__', '_')
                snake_case_entry[snake_key] = value
            snake_case_data.append(snake_case_entry)
        return snake_case_data

    def update_key_names(data):
        key_json_data = []
        for entry in data:
            updated_entry = {
                key.replace('please_state_any_medical_conditions_which_may_be_aggravated_by_exercise', 'medical_conditions')
                   .replace('please_check_any_of_the_following_that_apply', 'medical_checklist'): value for key, value in entry.items()
            }
            key_json_data.append(updated_entry)
        return key_json_data

    def separate_instances(data):
        separated_data = []
        # Define the repeating fields
        repeating_fields = ['full_name', 'date_of_birth', 'medical_conditions', 'medical_checklist', 'allergy', 'other']

        for entry in data:
            # Identify the highest instance number for repeating fields
            max_instances = max([int(k.split('.')[-1]) for k in entry.keys() if '.' in k] + [0])
            
            # Create separate entries for base and numbered instances
        for i in range(max_instances + 1):
            instance_entry = {}
            # Copy non-repeating fields to every instance
            for k, v in entry.items():
                if not any(k.startswith(field + '.') for field in repeating_fields):
                    instance_entry[k] = v
            
            # Add the repeating fields, adjusting for base and numbered instances
            for field in repeating_fields:
                field_name = f"{field}.{i}" if i > 0 else field
                if field_name in entry:
                    instance_entry[field] = entry[field_name]
                elif i == 0:
                    # For the base case, ensure all repeating fields are present even if they're empty
                    instance_entry[field] = entry.get(field, None)
            
            # Only add the instance if it has any of the repeating fields filled
            if any(field in instance_entry for field in repeating_fields):
                separated_data.append(instance_entry)

        return separated_data
    
    def format_dates(data):
        date_formatted_json_data = []
        for entry in data:
            for key, value in entry.items():
                if "date" in key and isinstance(value, str):  # Check if the field likely contains a date and is a string
                    # Initialize formatted_date as None
                    formatted_date = None
                    
                    # List of known date formats to try
                    date_formats = ["%b %d, %Y", "%d/%m/%Y", "%Y-%m-%d"]  # Add other known formats as needed
                    
                    # Try parsing the date with each known format
                    for date_format in date_formats:
                        try:
                            date_obj = datetime.strptime(value, date_format)
                            formatted_date = date_obj.strftime("%d/%m/%Y")
                            break  # Exit the loop on successful parsing
                        except ValueError:
                            pass  # Try the next format if parsing fails
                    
                    # Update the entry with the formatted date if parsing was successful
                    if formatted_date:
                        entry[key] = formatted_date
                    else:
                        # Log or handle dates that couldn't be formatted
                        print(f"Could not format date for {key}: {value}. Unrecognized format.")
            
            date_formatted_json_data.append(entry)
        return date_formatted_json_data


    
    def handle_multiline_medical_checklist(data):
        multiline_json_data = []
        for entry in data:
            new_entry = entry.copy()  # Make a copy to avoid modifying the original entry
            medical_checklist = new_entry.get('medical_checklist', '')
            if isinstance(medical_checklist, str):
                # Split the multiline string into a list by newline characters
                new_entry['medical_checklist'] = medical_checklist.split('\n')
            multiline_json_data.append(new_entry)
        return multiline_json_data
    
    def uppercase_string_fields(data):
        uppercase_data = []
        for entry in data:
            new_entry = {}
            for key, value in entry.items():
                # Check if the field is a string and the key is not 'email' or 'signed'
                if isinstance(value, str) and key != 'email' and key != 'signed':
                    new_entry[key] = value.upper()  # Convert to uppercase
                else:
                    new_entry[key] = value
            uppercase_data.append(new_entry)
        return uppercase_data
    
    def ensure_leading_zero_for_phones(data):
        phone_fields = ['phone', 'mobile', 'emergency_contact_phone']  # List of phone-related fields
        phone_json_data = []
        for entry in data:
            new_entry = {}
            for key, value in entry.items():
                # Check if the field is one of the phone-related fields
                if key in phone_fields and isinstance(value, int):
                    # Convert the number to a string and ensure it starts with a leading zero
                    new_entry[key] = "0" + str(value)
                else:
                    new_entry[key] = value
            phone_json_data.append(new_entry)
        return phone_json_data
    
    def split_address(data):
        address_json_data = []
        for entry in data:
            new_entry = entry.copy()  # Make a copy to avoid modifying the original entry directly
            address = new_entry.get('address', '')
            if ',' in address:
                # Split the address into AddressLine1 and postcode
                address_parts = address.rsplit(',', 1)  # Split from the right to ensure we only split on the last comma
                address_line_1, postcode = address_parts[0].strip(), address_parts[1].strip()
                
                # Further split AddressLine1 to separate the town, which is assumed to be the last word
                if ' ' in address_line_1:
                    *address_line_1_parts, town = address_line_1.rsplit(' ', 1)
                    address_line_1 = ' '.join(address_line_1_parts)
                else:
                    town = ''  # In case there's no identifiable town component
                
                # Create a nested structure for the address with town included
                new_entry['address'] = {
                    'address_line_1': address_line_1,
                    'town': town,
                    'postcode': postcode
                }
            address_json_data.append(new_entry)
        return address_json_data



    json_data = xlsx_to_json(input_xlsx_file)
    snake_case_json_data = convert_keys_to_snake_case(json_data)
    key_json_data = update_key_names(snake_case_json_data)
    separated_json_data = separate_instances(key_json_data)
    date_formatted_json_data = format_dates(separated_json_data)
    multiline_json_data = handle_multiline_medical_checklist(date_formatted_json_data)
    uppercase_json_data = uppercase_string_fields(multiline_json_data)
    phone_json_data = ensure_leading_zero_for_phones(uppercase_json_data)
    address_json_data = split_address(phone_json_data)

    with open(output_json_file, 'w') as file:
        json.dump(address_json_data, file, indent=4)

# Specify the actual input and output file paths when using the function.
clean_data('sample_input.xlsx', 'output.json')
