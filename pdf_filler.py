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
        # Signature
        signed = entry['signed']

        

        # Read the template PDF
        template_pdf = PdfReader(template_path)

        # Create a PDF file for each entry
        pdf_file_path = os.path.join(output_directory, f"{full_name}_form.pdf").upper()
        
        # Initialize a PdfWriter object for writing to a new PDF
        writer = PdfWriter()

        # Copy all pages from the template to the new file
        for page in template_pdf.pages:
            writer.add_page(page)

        # Create a packet for new PDF with reportlab
        packet = io.BytesIO()
        can = canvas.Canvas(packet, pagesize=letter)
        can.setFont("Helvetica", 9)
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

        can.drawString(100, 600, f"{medical_checklist}") # Signed by instructor

        # Medical checklist box rendering
        if "Heart Trouble" in medical_checklist:
            can.rect(40, 527, 58, 13)
        if "Migraine" in medical_checklist:
            can.rect(40, 512, 40, 13)
        if "Asthma" in medical_checklist:
            can.rect(40, 497, 37, 13)
        if "ADD / ADHD" in medical_checklist:
            can.rect(40, 482, 55, 13)
        if "High Blood Pressure" in medical_checklist:
            can.rect(160, 527, 85, 13)
        if "Haemophilia" in medical_checklist:
            can.rect(160, 512, 55, 13)
        if "Seizures" in medical_checklist:
            can.rect(160, 497, 43, 13)
        if "Back Pain" in medical_checklist:
            can.rect(160, 482, 44, 13)
        if "Chest Pains" in medical_checklist:
            can.rect(285, 527, 50, 13)
        if "Diabetes" in medical_checklist:
            can.rect(285, 512, 40, 13)
        if "HIV" in medical_checklist:
            can.rect(285, 497, 23, 13)
        if "Hay Fever" in medical_checklist:
            can.rect(285, 482, 45, 13)
        if "Nervous Disorders" in medical_checklist:
            can.rect(397, 527, 82, 13)
        if "Faint / Dizzy Spells" in medical_checklist:
            can.rect(397, 512, 80, 13)
        if "Hernia" in medical_checklist:
            can.rect(397, 497, 40, 13)

        can.setFont("Helvetica", 15)
        # Conditional rendering for media consent
        can.drawString(315, 355, "X") if media_consent.upper() == "YES" else can.drawString(362, 355, "X")
         

        # Conditional rendering for conviction
        can.drawString(315, 329, "X") if convicted.upper() == "YES" else can.drawString(362, 329, "X")
        
        can.setFont("Helvetica", 9)
        can.drawString(150, 315, f"{convicted_details}")
        can.drawString(320, 228, f"{source}")
        
        


        can.setFont("Helvetica", 16)
        can.drawString(260, 95, f"William Watson")
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
create_pdfs_from_json('jotform_api/data_files/cleaned_sub_data.json', 'pdfs', 'templates/InductionForm.pdf')
