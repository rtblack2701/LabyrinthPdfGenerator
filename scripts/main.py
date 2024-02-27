import csv_to_json
import pdf_gen

def generate_induction_pdfs(input_csv, output_csv, output_pdf_directory):
    csv_to_json.csv_to_json(input_csv, output_csv)
    pdf_gen.create_pdfs_from_json(output_csv, output_pdf_directory)


# Run pdf generator
generate_induction_pdfs('sample_input.csv', 'sample_output.json', 'pdfs')