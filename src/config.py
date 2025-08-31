import logging
import os
from datetime import datetime


# === Default parameters ===
DEFAULT_INPUT = os.getenv("DATASET_DIR", "../data/larfield")
DEFAULT_OUTPUT = os.getenv("DATASET_DIR", "../data/larfield")
DEFAULT_SAMPLING_RATE = 130
DEFAULT_VERBOSE = False


LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)
log_filename = os.path.join(LOG_DIR, f"log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)
console_handler = logging.StreamHandler()
file_handler = logging.FileHandler(log_filename)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)
logger.addHandler(console_handler)
logger.addHandler(file_handler)