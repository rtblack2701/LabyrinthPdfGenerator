import json

# Load the JSON data from the file
with open('jotform_api/data_files/jotform_submissions.json', 'r') as file:
    submissions_data = json.load(file)

# Filter only active submissions
active_submissions = [submission for submission in submissions_data['content'] if submission['status'] == 'ACTIVE']

def build_detailed_objects(submissions):
    detailed_objects = []

    for submission in submissions:
        start_date_info = submission['answers']['5']['answer']
        start_date = start_date_info.get('prettyFormat', 
                                         f"{start_date_info.get('year', '')}-{start_date_info.get('month', '')}-{start_date_info.get('day', '')}")
        
        address_info = submission['answers']['71']['answer']
        address = address_info.get('prettyFormat', f"{address_info.get('addr_line1', '')}, {address_info.get('city', '')}")
        postcode = address_info.get('prettyFormat', f"{address_info.get('postal', '')}")
       
        # Extract common fields for the submission
        common_fields = {
            "submission_id": submission['id'],
            "start_date": start_date,
            "email": submission['answers']['12'].get('answer', ''),
            "contact_name": submission['answers']['14'].get('answer', ''),
            "convicted_details": submission['answers']['35'].get('answer', ''),
            "source": submission['answers']['70'].get('answer', ''),
            "address": address,
            "postcode": postcode,
            "phone": submission['answers']['72'].get('answer', ''),
            "relationship": submission['answers']['75'].get('answer', ''),
            "emergency_contact_phone": submission['answers']['76'].get('answer', ''),
            "mobile": submission['answers']['78'].get('answer', ''),
            "consent": submission['answers']['79'].get('answer', ''),
            "convicted": submission['answers']['80'].get('answer', '')
        }

        # Initialize three objects for the participants
        objects = [{**common_fields}, {**common_fields}, {**common_fields}]
        
        for key, value in submission['answers'].items():
            if 'name' in value:
                if value['name'].startswith('p1_'):
                    objects[0][value['name']] = value.get('answer', '')
                elif value['name'].startswith('p2_'):
                    objects[1][value['name']] = value.get('answer', '')
                elif value['name'].startswith('p3_'):
                    objects[2][value['name']] = value.get('answer', '')
        
        detailed_objects.extend(objects)

    return detailed_objects



# Build the detailed objects
detailed_objects = build_detailed_objects(active_submissions)

# Write the detailed objects to a new JSON file
output_file_path = 'jotform_api/data_files/processed_submissions.json'
with open(output_file_path, 'w') as outfile:
    json.dump(detailed_objects, outfile, indent=4)

print(output_file_path)
