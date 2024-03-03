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
    start_time = time.time()  # Capture start time
    # 1. Get the form submission data
    run_script(["python", "-m", "jotform_api.api_endpoints.get_form_submissions"])
    
    # 2. Build the JSON file
    run_script(["python", "-m" "scripts.object_builder"])
    
    # 3. Clean the JSON file
    run_script(["python", "-m" "scripts.api_data_cleaner"])
    
    # If the cleaned_submission_data.json file is not empty, proceed with the following steps
    if check_for_empty_data('jotform_api/data_files/cleaned_submission_data.json'):
        print("No induction forms to process.")
        return  # Exit the main function early if there are no forms to process


    # 4. Generate the PDFs
    run_script(["python", "-m" "scripts.pdf_filler"])
    
    # 5. Overlay the PDFs with parent/guardian and coach signatures
    run_script(["python", "-m", "scripts.signature_overlay"])

    # HANDLE POST PROCESSING STEPS

    # 1. Update the list of processed submissions
    run_script(["python", "-m", "scripts.post_process_scripts.log_processed_submissions"])

    # 2. Zip the PDFs
    run_script(["python", "-m", "scripts.post_process_scripts.zip_email_pdfs"])

    # 3. Clean up the directories
    run_script(["python", "-m", "scripts.post_process_scripts.generated_file_removal"])

    end_time = time.time()  # Capture end time
    total_time = end_time - start_time  # Calculate total duration
    print(f"Total process time: {total_time:.2f} seconds")

if __name__ == "__main__":
    main()
