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
        submission_date = entry['submission_date']
        start_date = entry['start_date']
        # Participant-specific details
        full_name = entry['full_name']
        date_of_birth = entry['date_of_birth']
        medical_conditions = entry['medical_conditions']
        medical_checklist = entry['medical_checklist']
        allergy = entry['allergy']
        other = entry['other']
        # Parent/guardian details + contact information
        contact_name = entry['contact_name']
        phone = entry['phone']
        mobile = entry['mobile']
        email = entry['email']
        emergency_contact_phone = entry['emergency_contact_phone']
        relationship = entry['relationship']
        address_line_1 = entry['address']['address_line_1']
        town = entry['address']['town']
        postcode = entry['address']['postcode']
        # Consent, background, and media release
        media_consent = entry['media_consent']
        convicted = entry['convicted']
        conviction_details = entry['conviction_details']
        source = entry['source']
        # Signature
        signed = entry['signed']

        

        # Read the template PDF
        template_pdf = PdfReader(template_path)

        # Create a PDF file for each entry
        pdf_file_path = os.path.join(output_directory, f"{full_name}_form.pdf")
        
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
        can.drawString(360, 570, f"{medical_conditions}")
        #can.drawString(85, 665, f"{medical_checklist}")
        can.drawString(430, 488, f"{allergy}")
        can.drawString(80, 470, f"{other}")
        can.drawString(160, 614, f"{contact_name} ({relationship})")
        can.drawString(440, 692, f"{phone}")
        can.drawString(440, 674, f"{mobile}")
        can.drawString(110, 656, f"{email}")
        can.drawString(440, 614, f"{emergency_contact_phone}")
        can.drawString(85, 692, f"{address_line_1}, {town}")
        can.drawString(310, 674, f"{postcode}")

        
        # Conditional rendering for media consent
        if media_consent.upper() == "YES":
            can.drawString(317, 357, "X")  
        elif media_consent.upper() == "NO (IF YOU DO NOT CONSENT PLEASE MAKE YOUR INSTRUCTOR AWARE OF THIS)":
            can.drawString(364, 357, "X")  

        # Conditional rendering for conviction
        if convicted.upper() == "YES":
            can.drawString(317, 331, "X")  
        elif convicted.upper() == "NO":
            can.drawString(364, 331, "X") 
        
        #can.drawString(85, 547, f"{convicted}")
        can.drawString(150, 315, f"{conviction_details}")
        can.drawString(320, 228, f"{source}")
        #can.drawString(80, 290, f"{signed}")
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
create_pdfs_from_json('output.json', 'pdfs', 'templates/InductionForm.pdf')
