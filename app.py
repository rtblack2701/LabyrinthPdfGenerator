from flask import Flask, request, render_template, send_from_directory, after_this_request
import os
from werkzeug.utils import secure_filename
import shutil
import tempfile

# Assuming the existence of the following functions
from scripts.csv_to_json import csv_to_json  # Convert CSV to JSON
from scripts.pdf_gen import create_pdfs_from_json  # Generate PDFs from JSON

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')  # Assume you have an upload form in 'upload.html'

@app.route('/upload', methods=['POST'])
def upload_and_process():
    if 'file' not in request.files:
        return 'No file part', 400
    file = request.files['file']
    if file.filename == '':
        return 'No selected file', 400

    # Secure the filename and create a temporary directory for processing
    filename = secure_filename(file.filename)
    temp_dir = tempfile.mkdtemp()
    csv_path = os.path.join(temp_dir, filename)
    file.save(csv_path)

    # Convert CSV to JSON
    json_path = os.path.join(temp_dir, 'data.json')
    csv_to_json(csv_path, json_path)

    # Generate PDFs
    pdf_output_dir = os.path.join(temp_dir, 'pdfs')
    os.makedirs(pdf_output_dir, exist_ok=True)
    create_pdfs_from_json(json_path, pdf_output_dir)

    # Create a ZIP archive of the PDF directory
    zip_path = os.path.join(temp_dir, 'output.zip')
    shutil.make_archive(base_name=zip_path.replace('.zip', ''), format='zip', root_dir=pdf_output_dir)

    @after_this_request
    def cleanup(response):
        shutil.rmtree(temp_dir)  # Clean up the temp directory after sending the file
        return response

    return send_from_directory(directory=os.path.dirname(zip_path), filename=os.path.basename(zip_path), as_attachment=True, attachment_filename='generated_pdfs.zip')

if __name__ == '__main__':
    app.run(debug=True)
