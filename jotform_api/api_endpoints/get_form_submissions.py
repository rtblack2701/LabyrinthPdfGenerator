import requests
import json
from config_loader import load_config
from jotform import JotformAPIClient

apiKey, form_id = load_config()

# API endpoint
url = f'https://eu-api.jotform.com/form/{form_id}/submissions'

# API key
params = {
    'apiKey': apiKey,
}

# Make the GET request
response = requests.get(url, params=params)

# Check if the request was successful
if response.status_code == 200:
    # Parse the JSON response
    data = response.json()
    print("Request successful. Data received:")
    
    # Define the file path
    file_path = 'jotform_api/data_files/jotform_submissions.json'
    
    # Write the data to a JSON file
    with open(file_path, 'w') as json_file:
        json.dump(data, json_file, indent=4)
    
    print(f"Data has been written to {file_path}")
else:
    print(f"Request failed with status code: {response.status_code}")
