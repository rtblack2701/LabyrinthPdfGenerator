import os
import json
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import io

def overlay_signature(pdf_path, signature_image_path, coaches_signature_path, output_pdf_path, signature_coords, coaches_signature_coords):
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=letter)
    
    # Overlay the dynamic signature
    can.drawImage(signature_image_path, *signature_coords, mask='auto')
    
    # Overlay the coaches' signature
    can.drawImage(coaches_signature_path, *coaches_signature_coords, mask='auto')
    
    can.save()

    packet.seek(0)
    signature_pdf = PdfReader(packet)

    original_pdf = PdfReader(pdf_path)
    writer = PdfWriter()

    page = original_pdf.pages[0]
    page.merge_page(signature_pdf.pages[0])
    writer.add_page(page)

    for i in range(1, len(original_pdf.pages)):
        writer.add_page(original_pdf.pages[i])

    with open(output_pdf_path, 'wb') as output_file:
        writer.write(output_file)

def load_signature_mappings(json_file_path):
    with open(json_file_path, 'r') as file:
        data = json.load(file)
    
    # Create a mapping of submission_id to signature_image_path
    signature_mappings = {}
    for submission in data:
        submission_id = submission['submission_id']
        signature_image_path = f"{submission_id}_signature.png"  # Assuming signature images are named as such
        signature_mappings[submission_id] = signature_image_path
    print("Confirming" + {signature_mappings})
    return signature_mappings
    

def process_all_pdfs(pdf_directory, signatures_directory, output_directory, signature_coords, coaches_signature_path, coaches_signature_coords, json_file_path):
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    signature_mappings = load_signature_mappings(json_file_path)

    for pdf_file in os.listdir(pdf_directory):
        if pdf_file.endswith(".PDF"):
            submission_id = pdf_file.split("_")[0]

            signature_image_filename = signature_mappings.get(submission_id)
            if signature_image_filename:
                signature_image_path = os.path.join(signatures_directory, signature_image_filename)

                if os.path.exists(signature_image_path):
                    output_pdf_path = os.path.join(output_directory, pdf_file)
                    pdf_path = os.path.join(pdf_directory, pdf_file)
                    overlay_signature(pdf_path, signature_image_path, coaches_signature_path, output_pdf_path, signature_coords, coaches_signature_coords)
                    print(f"Processed {pdf_file}")
                else:
                    print(f"Signature image not found for {pdf_file} (submission ID: {submission_id})")
            else:
                print(f"No signature mapping found for {pdf_file} (submission ID: {submission_id})")

# Example usage - Adjust the paths and signature coordinates as needed
pdf_directory = 'assets/pdfs/pre_signed'
signatures_directory = 'assets/signature_images'
output_directory = 'assets/pdfs/post_signed'
json_file_path = 'jotform_api/data_files/cleaned_submission_data.json'
signature_coords = (90, 285, 145, 23)  # Example coordinates (x, y, width, height)
coaches_signature_path = 'assets/coach_signature.png'
coaches_signature_coords = (230, 70, 180, 50)  # Adjust these coordinates as needed

process_all_pdfs(pdf_directory, signatures_directory, output_directory, signature_coords, coaches_signature_path, coaches_signature_coords, json_file_path)



