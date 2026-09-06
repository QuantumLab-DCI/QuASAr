import logging
import os
from pathlib import Path

# Resolve paths locally to avoid importing app during logger initialization.
BASE_DIR = Path(__file__).resolve().parent.parent.parent
LOG_FILE = os.path.join(BASE_DIR, "data", "hqc_audit.log")

def get_logger():
    """Configure and return the audit logger."""
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

    logger = logging.getLogger("hqc_audit")
    
    # Avoid duplicate output when the application factory runs more than once.
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        
        formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        
        file_handler = logging.FileHandler(LOG_FILE, encoding='utf-8')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
    return logger
