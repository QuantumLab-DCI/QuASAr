import logging
import os
from pathlib import Path

# --- Independent Path Configuration ---
# This avoids importing 'app' and prevents circular import errors
# Current path: Backend/app/core/audit_logger.py
# .parent -> core
# .parent.parent -> app
# .parent.parent.parent -> Backend (project root)
BASE_DIR = Path(__file__).resolve().parent.parent.parent
LOG_FILE = os.path.join(BASE_DIR, "data", "hqc_audit.log")

def get_logger():
    """Configure and return the audit logger."""
    # Ensure that the data directory exists
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

    logger = logging.getLogger("hqc_audit")
    
    # Singleton pattern: do not add handlers again if they already exist
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        
        # Format: [DATE] [LEVEL] MESSAGE
        formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        
        # File handler
        file_handler = logging.FileHandler(LOG_FILE, encoding='utf-8')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        # Console handler (displays logs in the terminal when running run.py)
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
    return logger
