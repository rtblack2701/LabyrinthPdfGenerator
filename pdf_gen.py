from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import json
import os

def create_pdfs_from_json(json_file_path, output_directory):
    # Create the output directory if it doesn't exist
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    with open(json_file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    for entry in data:
        start_date = entry['start_date']
        participant = entry['participant']
        parent = entry['parent']
        address = entry['address']

        # Create a PDF file for each entry in the specified output directory
        pdf_file_path = os.path.join(output_directory, f"{kid}_form.pdf")
        c = canvas.Canvas(pdf_file_path, pagesize=letter)
        c.drawText(100, 800, f"Lurgan & Tandragee Ju-Jitsu Club")
        c.drawString(100, 800, f"Start Date: {start_date}")
        c.drawString(100, 750, f"{participant}")
        c.drawString(100, 730, f"Parent: {parent}")
        c.drawString(100, 710, f"Address: {address}")
        c.save()

# Example usage
create_pdfs_from_json('output.json', 'pdfs')
