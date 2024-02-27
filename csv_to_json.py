import csv
import json

def csv_to_json(csv_file_path, json_file_path):
    data = []
    try:
        with open(csv_file_path, mode='r', encoding='utf-8') as csvfile:
            csv_reader = csv.DictReader(csvfile)
            for row in csv_reader:
                names = row['names'].split(',')
                dobs = row['dob'].split(',')
                for name, dob in zip(names, dobs):
                    kid_data = {
                        'start_date': row['start_date'],
                        'name': name.strip(),
                        'parent': row['parent'],
                        'address': row['address'],
                        'dob': dob.strip(),
                    }
                    data.append(kid_data)
    except KeyError as e:
        print(f"KeyError: Check your CSV column names. Missing key: {e}")
        return
    
    with open(json_file_path, 'w', encoding='utf-8') as jsonfile:
        json.dump(data, jsonfile, indent=4)

# Replace 'input.csv' and 'output.json' with your actual file paths
csv_to_json('sample_input.csv', 'output.json')
