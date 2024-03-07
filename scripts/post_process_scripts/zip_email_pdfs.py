import os
from zipfile import ZipFile
from datetime import datetime
import glob

# Get current date to use in file names
current_date = datetime.now().strftime("%Y-%m-%d")

# Step 2: Zip the PDF files
def zip_files(directory="assets/pdfs/post_signed", zip_name=f"LTJJC_InductionForms-{current_date}.zip"):
    files = glob.glob(f"{directory}/*.PDF")  # Adjusted to select only .PDF files
    with ZipFile(zip_name, 'w') as zipf:
        for file in files:
            zipf.write(file, os.path.basename(file))
    return zip_name

zip_file = zip_files()

