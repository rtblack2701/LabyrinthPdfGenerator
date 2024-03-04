import json
import requests
import os

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
            print(f"Image saved successfully as: {save_path}")
            return True
        else:
            print(f"Failed to download image. Status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"An error occurred: {e}")
        return False

def extract_value_by_name(answers, name_key):
    for key, value in answers.items():
        if value.get('name') == name_key:
            # Ensure it returns a dictionary with 'answer' even if it's just an empty string
            return {'answer': value.get('answer', '')}
    # Return a default dictionary with an empty 'answer' if no match is found
    return {'answer': ''}


def build_detailed_objects(submissions):
    detailed_objects = []

    for submission in submissions:
        answers = submission['answers']
        start_date_info = extract_value_by_name(answers, 'start_date')['answer']
        start_date = start_date_info.get('prettyFormat', 
                                         f"{start_date_info.get('year', '')}-{start_date_info.get('month', '')}-{start_date_info.get('day', '')}")
        
        address_info = extract_value_by_name(answers, 'address')['answer']
        address = address_info.get('prettyFormat', f"{address_info.get('addr_line1', '')}, {address_info.get('city', '')}")
        postcode = address_info.get('prettyFormat', f"{address_info.get('postal', '')}")
       
        # Extract common fields for the submission
        common_fields = {
            "submission_id": submission['id'],
            "created_at": submission['created_at'],
            "start_date": start_date,
            "email": extract_value_by_name(answers, 'email')['answer'],
            "contact_name": extract_value_by_name(answers, 'contact_name')['answer'],
            "convicted_details": extract_value_by_name(answers, 'convicted_details')['answer'],
            "source": extract_value_by_name(answers, 'source')['answer'],
            "address": address,
            "postcode": postcode,
            "phone": extract_value_by_name(answers, 'phone')['answer'],
            "relationship": extract_value_by_name(answers, 'relationship')['answer'],
            "emergency_contact_phone": extract_value_by_name(answers, 'emergency_contact_phone')['answer'],
            "mobile": extract_value_by_name(answers, 'mobile')['answer'],
            "consent": extract_value_by_name(answers, 'consent')['answer'],
            "convicted": extract_value_by_name(answers, 'convicted')['answer'],
            "signed": extract_value_by_name(answers, 'signed')['answer'],
        }

        signed_url = common_fields['signed']
        if signed_url:
            save_path = os.path.join(signature_images_directory, f"{submission['id']}_signature.png")
            if save_image_from_url(signed_url, save_path):
                # Update the common fields with the path to the saved image
                common_fields['signature_image_path'] = save_path

        # Initialize three objects for the participants
        objects = [{**common_fields}, {**common_fields}, {**common_fields}]
        
        for key, value in submission['answers'].items():
            if 'name' in value:
                field_name = value['name']
                if field_name.startswith('p') and 'dob' in field_name:
                    dob = value.get('answer', {})
                    formatted_dob = f"{dob.get('day', '')}/{dob.get('month', '')}/{dob.get('year', '')}"
                    participant_index = int(field_name[1]) - 1
                    objects[participant_index][field_name] = formatted_dob
                else:
                    if field_name.startswith('p1_'):
                        objects[0][field_name] = value.get('answer', '')
                    elif field_name.startswith('p2_'):
                        objects[1][field_name] = value.get('answer', '')
                    elif field_name.startswith('p3_'):
                        objects[2][field_name] = value.get('answer', '')

        detailed_objects.extend(objects)

    return detailed_objects

# Load the JSON data from the file
with open('jotform_api/data_files/jotform_api_submissions.json', 'r') as file:
    submissions_data = json.load(file)

# Filter only active submissions
active_submissions = [submission for submission in submissions_data['content'] if submission['status'] == 'ACTIVE']

# Build the detailed objects
detailed_objects = build_detailed_objects(active_submissions)

# Write the detailed objects to a new JSON file
output_file_path = 'jotform_api/data_files/built_form_submission.json'
with open(output_file_path, 'w') as outfile:
    json.dump(detailed_objects, outfile, indent=4)

print(output_file_path)
