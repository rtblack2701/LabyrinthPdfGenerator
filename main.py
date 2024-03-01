import subprocess

def run_script(command):
    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {command}\nError: {e}")

def main():
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

if __name__ == "__main__":
    main()
