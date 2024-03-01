# Labyrinth PDF Generator

## Purpose
Python application designed to allow one parent/guardian to fill out a single membership form for multiple children and generate a separate PDF form for each child.

## Installation
1. Clone the repository: `git@github.com:rtblack2701/LabyrinthPdfGenerator.git`
2. Install the required packages: `pip install -r requirements.txt`
3. Run the application: 
    - Copy your CSV file to the root directory
    - Update the `scripts/main.py` file to point to the correct `input_csv` file:
        - `generate_induction_pdfs('sample_input.csv', 'sample_output.json', 'pdfs')`
    - `python ~/path/to/LabyrinthPdfGenerator/scripts/main.py`
    - Inspect the generated pdfs in the `pdfs` directory

## Usage

### First-time use
Authenticate with Jotform API:
`python -m jotform_api/api_endpoints/authentication`

#### Then:
1. Get the form submission data:
    `python -m jotform_api.api_endpoints.get_form_submissions`
2. Build the JSON file:
    `python scripts/object_builder`
3. Clean the JSON file:
    `python scripts/api_data_cleaner`
4. Generate the PDFs:
    `python scripts/pdf_filler`
5. Overlay the PDFs with parent/guardian and coach signatures:
    `python -m scripts/signature_overlay`



// TODO: Add better messaging and error handling to api_data_cleaner.py