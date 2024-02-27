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