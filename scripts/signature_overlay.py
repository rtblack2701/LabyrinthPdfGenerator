import os
import json
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import io

def overlay_signature(pdf_path, signature_details, output_pdf_path):
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=letter)
    
    for image_path, coords in signature_details:
        can.drawImage(image_path, *coords, mask='auto')
    can.save()

    packet.seek(0)
    new_pdf = PdfReader(packet)
    original_pdf = PdfReader(pdf_path)
    writer = PdfWriter()

    original_pdf.pages[0].merge_page(new_pdf.pages[0])
    for page in original_pdf.pages:
        writer.add_page(page)

    with open(output_pdf_path, 'wb') as output_file:
        writer.write(output_file)

def load_signature_mappings(json_file_path):
    with open(json_file_path, 'r') as file:
        data = json.load(file)
        signature_mappings = {}
        for submission_list in data:  # Iterate over outer list
            for submission in submission_list:  # Iterate over each submission
                submission_id = submission['submission_id']
                # Use the signature_image_path directly from the submission
                signature_image_path = submission['signature_image_path']
                # Extract the filename and map it to the submission_id
                signature_mappings[submission_id] = os.path.basename(signature_image_path)
        return signature_mappings
    
def process_all_pdfs(pdf_directory, signatures_directory, output_directory, signature_coords, coaches_signature_path, coaches_signature_coords, json_file_path):
    os.makedirs(output_directory, exist_ok=True)
    signature_mappings = load_signature_mappings(json_file_path)

    for pdf_file in filter(lambda f: f.endswith(".PDF"), os.listdir(pdf_directory)):
        submission_id, *_ = pdf_file.split("_")
        signature_image_filename = signature_mappings.get(submission_id)

        if signature_image_filename:
            signature_image_path = os.path.join(signatures_directory, signature_image_filename)
            if os.path.exists(signature_image_path):
                overlay_signature(
                    os.path.join(pdf_directory, pdf_file),
                    [(signature_image_path, signature_coords), (coaches_signature_path, coaches_signature_coords)],
                    os.path.join(output_directory, pdf_file)
                )
                print(f"Processed {pdf_file}")
            else:
                print(f"Signature image not found for {pdf_file} (submission ID: {submission_id})")
        else:
            print(f"No signature mapping found for {pdf_file} (submission ID: {submission_id})")

# Example usage - Adjust the paths and signature coordinates as needed
pdf_directory = 'assets/pdfs/pre_signed'
signatures_directory = 'assets/signature_images'
output_directory = 'assets/pdfs/post_signed'
json_file_path = 'jotform_api/data_files/submission_data.json'
signature_coords = (90, 285, 145, 23)  # Example coordinates (x, y, width, height)
coaches_signature_path = 'assets/coach_signature.png'
coaches_signature_coords = (230, 70, 180, 50)  # Adjust these coordinates as needed

process_all_pdfs(pdf_directory, signatures_directory, output_directory, signature_coords, coaches_signature_path, coaches_signature_coords, json_file_path)



