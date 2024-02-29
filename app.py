from flask import Flask, request, send_from_directory, render_template
import os
from xlsx_to_json import csv_to_json
from pdf_gen import create_pdfs_from_json
import shutil
import tempfile

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)
        if file:
            temp_dir = tempfile.mkdtemp()
            csv_path = os.path.join(temp_dir, 'input.csv')
            json_path = os.path.join(temp_dir, 'output.json')
            pdfs_dir = os.path.join(temp_dir, 'pdfs')
            zip_path = os.path.join(temp_dir, 'pdfs.zip')

            file.save(csv_path)
            csv_to_json(csv_path, json_path)
            create_pdfs_from_json(json_path, pdfs_dir)

            # Zip the PDF files
            shutil.make_archive(pdfs_dir, 'zip', pdfs_dir)

            return send_from_directory(directory=temp_dir, path='pdfs.zip', as_attachment=True)
        
        return render_template('index.html', message='PDF files have been successfully generated and downloaded.')

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
