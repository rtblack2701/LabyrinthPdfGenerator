import requests
from jotform_api.configuration.config_loader import load_config
from jotform import JotformAPIClient


apiKey, form_id = load_config()

# API endpoint
url = "https://eu-api.jotform.com/user"

# Parameters including the API key
params = {
    'apiKey': apiKey
}

# Make the GET request
response = requests.get(url, params=params)

# Check if the request was successful
if response.status_code == 200:
    # Parse the JSON response
    data = response.json()
    print("Request successful. Data received:")
    print(data)
else:
    print(f"Request failed with status code: {response.status_code}")
