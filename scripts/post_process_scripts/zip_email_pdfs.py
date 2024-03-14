import os
from zipfile import ZipFile
import fnmatch
from datetime import datetime

current_date = datetime.now().strftime("%Y-%m-%d")

def zip_files(directories, zip_name=f"LTJJC_InductionForms-{current_date}.zip"):
    with ZipFile(zip_name, 'w') as zipf:
        for directory in directories:
            files = os.listdir(directory)
            # Case-insensitive search for .pdf files
            pdf_files = fnmatch.filter(files, '*.PDF') + fnmatch.filter(files, '*.pdf')
            for file in pdf_files:
                file_path = os.path.join(directory, file)
                zipf.write(file_path, os.path.basename(file_path))
    return zip_name

# Example usage: Specify the list of directories you want to include in the zip
directories = [
    "assets/pdfs/summary_report",
    "assets/pdfs/post_signed"
]

zip_file = zip_files(directories)
print(f"Created zip file: {zip_file}")

