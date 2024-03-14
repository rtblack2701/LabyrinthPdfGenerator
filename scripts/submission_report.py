import json
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Spacer, Paragraph, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER

def load_submissions(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

def generate_pdf_report(submissions, report_path):
    # Initialize the PDF document and styles
    pdf = SimpleDocTemplate(report_path, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()

    # Custom Styles
    report_title_style = styles['Title'].clone('report_title_style')
    report_title_style.fontSize = 20
    report_title_style.textColor = colors.black

    header_style = ParagraphStyle(
        'header_style',
        parent=styles['Heading2'],
        fontSize=12,
        leading=14,
        spaceAfter=6,
        textColor=colors.black,
        alignment=TA_CENTER
    )

    # Report Title
    report_title = Paragraph('Submission Report Summary', report_title_style)

    # Flatten submissions
    flattened_submissions = [item for sublist in submissions for item in sublist]
    total_submissions = len(flattened_submissions)
    total_participants = sum(len(submission['participants']) for submission in flattened_submissions)

    # Prepare table data
    table_data = [[
        Paragraph('Participant Name', styles['Heading3']),
        Paragraph('Start Date', styles['Heading3']),
        Paragraph('Created At', styles['Heading3']),
        Paragraph('Date of Birth', styles['Heading3'])
    ]]
    for submission in flattened_submissions:
        start_date = submission['start_date']
        created_at = submission['created_at']
        for participant in submission['participants']:
            table_data.append([
                participant['full_name'],
                start_date,
                created_at,
                participant['dob']
            ])

    # Sort table data by 'Created At' in descending order
    table_data[1:] = sorted(table_data[1:], key=lambda x: datetime.strptime(x[2], "%d/%m/%Y"), reverse=True)

    # Add elements to the document
    elements.append(report_title)
    elements.append(Spacer(1, 20))
    elements.append(Paragraph(f"Total Submissions: {total_submissions}", header_style))
    elements.append(Paragraph(f"Total Participants: {total_participants}", header_style))
    elements.append(Spacer(1, 20))

    # Table for Participant Data
    participant_table = Table(table_data, spaceBefore=12, spaceAfter=12)
    participant_table.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,0), 12),
        ('GRID', (0,0), (-1,-1), 1, colors.black),
        ('FONTNAME', (0,1), (-1,-1), 'Helvetica')
    ]))

    elements.append(participant_table)

    # Build the PDF
    pdf.build(elements)

# Example usage
file_path = 'jotform_api/data_files/submission_data.json'  # Update to your file path
report_path = 'assets/pdfs/summary_report/ReportSummary.pdf'
submissions = load_submissions(file_path)
generate_pdf_report(submissions, report_path)