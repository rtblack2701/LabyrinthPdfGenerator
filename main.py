from scripts.csv_to_json import csv_to_json
from scripts.pdf_gen import create_pdfs_from_json


def generate_induction_pdfs(input_csv, output_csv, output_pdf_directory):
    csv_to_json(input_csv, output_csv)
    create_pdfs_from_json(output_csv, output_pdf_directory)


# Run pdf generator
# generate_induction_pdfs('sample_input.csv', 'sample_output.json', 'pdfs')