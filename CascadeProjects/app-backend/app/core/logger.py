import logging
from logging.handlers import RotatingFileHandler
import os
from datetime import datetime

# Create logs directory if it doesn't exist
os.makedirs("logs", exist_ok=True)

# Create logger
logger = logging.getLogger("app")
logger.setLevel(logging.INFO)

# Create handlers
stream_handler = logging.StreamHandler()
file_handler = RotatingFileHandler(
    f"logs/app_{datetime.now().strftime('%Y%m%d')}.log",
    maxBytes=1024 * 1024 * 5,  # 5MB
    backupCount=5
)

# Create formatters and add to handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
stream_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

# Add handlers to the logger
logger.addHandler(stream_handler)
logger.addHandler(file_handler)

# Example usage:
# from app.core.logger import logger
# logger.info("This is an info message")
