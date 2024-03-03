import subprocess
import time

def run_script(command):
    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {command}\nError: {e}")

def main():
    start_time = time.time()  # Capture start time
    # 1. Get the form submission data
    run_script(["python", "-m", "jotform_api.api_endpoints.get_form_submissions"])
    
    # 2. Build the JSON file
    run_script(["python", "-m" "scripts.object_builder"])
    
    # 3. Clean the JSON file
    run_script(["python", "-m" "scripts.api_data_cleaner"])
    
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
