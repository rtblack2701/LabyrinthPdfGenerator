import os
import logging
from logging.handlers import RotatingFileHandler
import json

def prepend_log_entry(log_file, entry):
    """Prepend the log entry to the log file."""
    if os.path.exists(log_file):
        with open(log_file, 'r+', encoding='utf-8') as file:
            current_contents = file.read()
            file.seek(0, 0)  # Move to the start of the file
            file.write(entry + '\n' + current_contents)
    else:
        with open(log_file, 'w', encoding='utf-8') as file:
            file.write(entry + '\n')

def setup_logger(log_file):
    logger = logging.getLogger("CustomCleanupLog")
    logger.setLevel(logging.INFO)
    
    # Create a custom handler that uses our prepend function
    class PrependFileHandler(logging.Handler):
        def emit(self, record):
            log_entry = self.format(record)
            prepend_log_entry(log_file, log_entry)
            
    handler = PrependFileHandler()
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger

def cleanup_directories(directories_to_cleanup, file_extensions_to_delete, logger):
    deleted_assets = {
        'submission_data': [],
        'signature_files': [],
        'pdfs': []
    }
    pdf_names_tracker = {}
    failed_deletions = []

    for directory in directories_to_cleanup:
        if os.path.exists(directory):
            for filename in os.listdir(directory):
                if filename.endswith(tuple(file_extensions_to_delete)):
                    file_path = os.path.join(directory, filename)
                    try:
                        if os.path.isfile(file_path) or os.path.islink(file_path):
                            os.unlink(file_path)
                            category = None
                            if 'data_files' in file_path:
                                category = 'submission_data'
                            elif 'signature_images' in file_path:
                                category = 'signature_files'
                            elif 'pdfs' in file_path:
                                pdf_base_name = filename.lower()  # Normalize filename
                                if pdf_base_name not in pdf_names_tracker:
                                    pdf_names_tracker[pdf_base_name] = {'pre_signed': False, 'post_signed': False}
                                category = 'pdfs'
                                sub_category = 'pre_signed' if 'pre_signed' in file_path else 'post_signed'
                                pdf_names_tracker[pdf_base_name][sub_category] = True
                            
                            if category and category != 'pdfs':
                                deleted_assets[category].append(file_path)
                            elif category == 'pdfs' and pdf_base_name not in deleted_assets['pdfs']:
                                deleted_assets['pdfs'].append(pdf_base_name)

                    except Exception as e:
                        failed_deletions.append({"file": file_path, "reason": str(e)})

    # Finalize PDF deletion tracking and log errors for missing counterparts
    total_pdfs_deleted = sum((1 for info in pdf_names_tracker.values() if info['pre_signed'] and info['post_signed']))
    for pdf_name, locations in pdf_names_tracker.items():
        if not (locations['pre_signed'] and locations['post_signed']):
            error_msg = f"PDF {pdf_name} found only in {'pre_signed' if locations['pre_signed'] else 'post_signed'} directory."
            logger.error(error_msg)

    # Prepare the final log object
    final_log = {
        "deleted_assets_summary": {
            "submission_data": len(deleted_assets['submission_data']),
            "signature_files": len(deleted_assets['signature_files']),
            "pdfs": total_pdfs_deleted  # Just a count of PDFs deleted from both directories
        },
        "detailed_deletions": deleted_assets,
        "failed_deletions": failed_deletions
    }

    if any(value for key, value in deleted_assets.items() if key != 'pdfs') or total_pdfs_deleted > 0 or failed_deletions:  # Check if there's anything to log
        logger.info(json.dumps(final_log, indent=4))


if __name__ == "__main__":
    directories_to_cleanup = [
        'jotform_api/data_files',
        'assets/signature_images',
        'assets/pdfs/pre_signed',
        'assets/pdfs/post_signed',
    ]
    file_extensions_to_delete = ['.PDF', '.pdf', '.json', '.png']

    log_file = 'cleanup_summary.log'
    logger = setup_logger(log_file)
    cleanup_directories(directories_to_cleanup, file_extensions_to_delete, logger)
