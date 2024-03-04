import requests
import json
from jotform_api.configuration.config_loader import load_encrypted_config
from jotform import JotformAPIClient

key_path = "jotform_api/configuration/encryption_key.key"
config_path = "jotform_api/configuration/encrypted_config_file.enc"

def fetch_api_data(api_key, form_id):
    """
    Fetches data from the JotForm API for a given form.

    Parameters:
    - api_key (str): The API key used for authentication.
    - form_id (str): The ID of the form to fetch submissions for.

    Returns:
    - dict: The JSON response from the API.

    Raises:
    - Exception: If the request fails with a non-200 status code.
    """
    url = f'https://eu-api.jotform.com/form/{form_id}/submissions'
    params = {'apiKey': api_key}
    response = requests.get(url, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Request failed with status code: {response.status_code}")

def write_data_to_file(data, file_path):
    with open(file_path, 'w') as json_file:
        json.dump(data, json_file, indent=4)
    print(f"Data has been written to {file_path}")

try:
    config = load_encrypted_config(key_path, config_path)
    api_key = config.get("JOTFORM_API_KEY")
    form_id = config.get("JOTFORM_LTJJC_INDUCTION_FORM_ID")

    if not api_key or not form_id:
        raise ValueError("API key or Form ID is missing. Please check the encrypted configuration.")

    # Proceed with fetching data and other operations
    data = fetch_api_data(api_key, form_id)
    write_data_to_file(data, 'jotform_api/data_files/jotform_api_submissions.json')
except Exception as e:
    print(f"Error: {e}")