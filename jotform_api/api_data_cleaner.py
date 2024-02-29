import json

# Correcting the previous approach to load the data first from the provided JSON file
file_path = 'jotform_submissions.json'

with open(file_path, 'r') as file:
    data = json.load(file)

# Now, let's filter the submissions to keep only those with an "ACTIVE" status
active_submissions_filtered = [submission for submission in data['content'] if submission['status'] == 'ACTIVE']

# Prepare to save the filtered submissions to a new JSON file
new_filtered_file_path = 'jotform_submissions.json'
with open(new_filtered_file_path, 'w') as file:
    json.dump({"content": active_submissions_filtered}, file, indent=4)

new_filtered_file_path

