
import logging
import os
from app.config import LOG_FILE, LOG_LEVEL

# Configure logging
logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

# Create a logger instance
logger = logging.getLogger("LoanApprovalSystem")
