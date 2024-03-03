from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
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
        # Check if 'full_name' is present and not empty for the participant
        if 'participant' in entry and entry['participant'][0].get('full_name'):
            submission_id = entry['submission_id']
            submission_date = entry['created_at']
            start_date = entry['start_date']
            # Participant-specific details
            full_name = entry['participant'][0]['full_name']
            date_of_birth = entry['participant'][0]['dob']
            medical_condition = entry['participant'][0]['medical_condition']
            medical_checklist = entry['participant'][0]['medical_checklist']
            allergy = entry['participant'][0]['allergy']
            other_medical = entry['participant'][0]['other_medical']
            # Parent/guardian details + contact information
            contact_name = entry['contact_name']
            phone = entry['phone']
            mobile = entry['mobile']
            email = entry['email']
            emergency_contact_phone = entry['emergency_contact_phone']
            relationship = entry['relationship'] 
            address = entry['address']
            postcode = entry['postcode']
            # Consent, background, and media release
            media_consent = entry['consent']
            convicted = entry['convicted']
            convicted_details = entry['convicted_details']
            source = entry['source']

            # Define medical conditions with their corresponding coordinates and dimensions
            medical_conditions = [
                {"name": "Heart Trouble", "x": 40, "y": 527, "width": 58, "height": 13},
                {"name": "Migraine", "x": 40, "y": 512, "width": 40, "height": 13},
                {"name": "Asthma", "x": 40, "y": 497, "width": 37, "height": 13},
                {"name": "ADD / ADHD", "x": 40, "y": 482, "width": 55, "height": 13},
                {"name": "High Blood Pressure", "x": 160, "y": 527, "width": 85, "height": 13},
                {"name": "Haemophilia", "x": 160, "y": 512, "width": 55, "height": 13},
                {"name": "Seizures", "x": 160, "y": 497, "width": 43, "height": 13},
                {"name": "Back Pain", "x": 160, "y": 482, "width": 44, "height": 13},
                {"name": "Chest Pains", "x": 285, "y": 527, "width": 50, "height": 13},
                {"name": "Diabetes", "x": 285, "y": 512, "width": 40, "height": 13},
                {"name": "HIV", "x": 285, "y": 497, "width": 23, "height": 13},
                {"name": "Hay Fever", "x": 285, "y": 482, "width": 45, "height": 13},
                {"name": "Nervous Disorders", "x": 397, "y": 527, "width": 82, "height": 13},
                {"name": "Faint / Dizzy Spells", "x": 397, "y": 512, "width": 80, "height": 13},
                {"name": "Hernia", "x": 397, "y": 497, "width": 40, "height": 13},
            ]

            # Read the template PDF
            template_pdf = PdfReader(template_path)

            # Create a PDF file for each entry
            pdf_preprocess_directory = os.path.join(output_directory)
            pdf_filename = f"{submission_id}_{full_name}_form.pdf".upper()
            pdf_file_path = os.path.join(pdf_preprocess_directory, pdf_filename)
        else:
            print(f"Skipping entry {entry['submission_id']} due to missing full name.")
        
        # Initialize a PdfWriter object for writing to a new PDF
        writer = PdfWriter()

        # Copy all pages from the template to the new file
        for page in template_pdf.pages:
            writer.add_page(page)

        # Create a packet for new PDF with reportlab
        packet = io.BytesIO()
        can = canvas.Canvas(packet, pagesize=letter)
        can.setFont('Helvetica', 9)
        can.drawString(85, 750, f"LURGAN & TANDRAGEE JU-JITSU CLUB")
        can.drawString(430, 288, f"{submission_date}") # Signed by parent/guardian date
        can.drawString(465, 93, f"{submission_date}") # Signed by instructor date
        can.drawString(330, 750, f"{start_date}")
        can.drawString(75, 710, f"{full_name}")
        can.drawString(440, 710, f"{date_of_birth}")
        can.drawString(360, 570, f"{medical_condition}")
        can.drawString(430, 488, f"{allergy}")
        can.drawString(80, 470, f"{other_medical}")
        can.drawString(160, 614, f"{contact_name} ({relationship})") # Emergency contact relationship
        can.drawString(455, 270, f"{relationship}") # Declaration of relationship
        can.drawString(440, 692, f"{phone}")
        can.drawString(440, 674, f"{mobile}")
        can.drawString(110, 656, f"{email}")
        can.drawString(440, 614, f"{emergency_contact_phone}")
        can.drawString(85, 692, f"{address}")
        can.drawString(310, 674, f"{postcode}")

        # Loop through each condition and render a box if it's in the checklist
        for condition in medical_conditions:
            if condition["name"] in medical_checklist:
                can.rect(condition["x"], condition["y"], condition["width"], condition["height"])

        can.setFont("Helvetica", 15)
        # Conditional rendering for media consent & conviction
        can.drawString(315, 355, "X") if media_consent.upper() == "YES" else can.drawString(362, 355, "X")
        can.drawString(315, 329, "X") if convicted.upper() == "YES" else can.drawString(362, 329, "X")
        
        can.setFont("Helvetica", 9)
        can.drawString(150, 315, f"{convicted_details}")
        can.drawString(320, 228, f"{source}")
        
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

try:
    create_pdfs_from_json('jotform_api/data_files/cleaned_submission_data.json', 'assets/pdfs/pre_signed', 'templates/InductionForm.pdf')
except Exception as e:
    print(f"Error creating PDFs: {e}")