from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from PyPDF2 import PdfReader, PdfWriter
import json
import os
import io

def create_pdfs_from_json(json_file_path, output_directory, template_path):
    # Create the output directory if it doesn't exist
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    with open(json_file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    for entry in data:
        start_date = entry['start_date']
        name = entry['name']
        parent = entry['parent']
        address = entry['address']
        dob = entry['dob']

        # Read the template PDF
        template_pdf = PdfReader(template_path)

        # Create a PDF file for each entry
        pdf_file_path = os.path.join(output_directory, f"{name}_form.pdf")
        
        # Initialize a PdfWriter object for writing to a new PDF
        writer = PdfWriter()

        # Copy all pages from the template to the new file
        for page in template_pdf.pages:
            writer.add_page(page)

        # Create a packet for new PDF with reportlab
        packet = io.BytesIO()
        can = canvas.Canvas(packet, pagesize=letter)
        can.drawString(500, 2000, f"Lurgan & Tandragee Ju-Jitsu Club")
        can.drawString(100, 800, f"Start Date: {start_date}")
        can.drawString(75, 710, f"{name}")
        can.drawString(100, 730, f"Parent: {parent}")
        can.drawString(85, 692, f"{address}")
        can.drawString(445, 710, f"{dob}")
        can.setFont("Courier-Oblique", 12)
        can.drawString(270, 95, f"William Watson")
        can.save()

        # Move to the beginning of the StringIO buffer
        packet.seek(0)
        new_pdf = PdfReader(packet)
        
        # Add the overlay from the new PDF to the existing page
        for i, page in enumerate(writer.pages):
            overlay_page = new_pdf.pages[i]
            page.merge_page(overlay_page)

        # Write to the output PDF file
        with open(pdf_file_path, 'wb') as output_pdf:
            writer.write(output_pdf)

# Example usage
create_pdfs_from_json('output.json', 'pdfs', 'templates/InductionForm.pdf')
