import os

def cleanup_directories(directories_to_cleanup, file_extensions_to_delete):
    for directory in directories_to_cleanup:
        if os.path.exists(directory):  # Check if the directory exists
            for filename in os.listdir(directory):
                if filename.endswith(tuple(file_extensions_to_delete)):
                    file_path = os.path.join(directory, filename)
                    try:
                        if os.path.isfile(file_path) or os.path.islink(file_path):
                            os.unlink(file_path)
                            print(f"Deleted {file_path}")
                        # Directories and non-matching file types are ignored
                    except Exception as e:
                        print(f"Failed to delete {file_path}. Reason: {e}")

# List of directories to clean up
directories_to_cleanup = [
    'jotform_api/data_files',
    'assets/signature_images',
    'assets/pdfs/pre_signed',
    'assets/pdfs/post_signed',
]

# List of file extensions to delete, e.g., ['.pdf', '.txt']
file_extensions_to_delete = ['.PDF', '.json', '.png']

cleanup_directories(directories_to_cleanup, file_extensions_to_delete)
