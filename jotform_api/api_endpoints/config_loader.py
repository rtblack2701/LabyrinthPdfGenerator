import json

def load_config():
    file_path = 'jotform_api/api_endpoints/api_creds.json'

    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
            return data['api_key'], data['form_id']
    except FileNotFoundError:
        raise FileNotFoundError(f"JSON file not found at {file_path}")
    except KeyError as e:
        raise KeyError(f"Missing key in JSON file: {e}")
