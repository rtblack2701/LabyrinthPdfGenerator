import subprocess
import time
import json

def run_script(command):
    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {command}\nError: {e}")

def check_for_empty_data(file_path):
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
            return len(data) == 0  # True if data is an empty list
    except (FileNotFoundError, json.JSONDecodeError):
        return True  # Treat missing or invalid files as empty

def main():
    start_time = time.time()
    run_script(["python", "-m", "jotform_api.api_endpoints.get_form_submissions"])
    run_script(["python", "-m", "scripts.object_builder"])
    run_script(["python", "-m", "scripts.api_data_cleaner"])
    
    if check_for_empty_data('jotform_api/data_files/cleaned_submission_data.json'):
        run_script(["python", "-m", "scripts.post_process_scripts.generated_file_removal"])
        print("No induction forms to process.")
        return
    
    run_script(["python", "-m", "scripts.pdf_filler"])
    run_script(["python", "-m", "scripts.signature_overlay"])
    run_script(["python", "-m", "scripts.post_process_scripts.log_processed_submissions"])
    run_script(["python", "-m", "scripts.post_process_scripts.zip_email_pdfs"])
    run_script(["python", "-m", "scripts.post_process_scripts.generated_file_removal"])

    end_time = time.time()
    total_time = end_time - start_time
    print(f"Total process time: {total_time:.2f} seconds")

if __name__ == "__main__":
    main()
