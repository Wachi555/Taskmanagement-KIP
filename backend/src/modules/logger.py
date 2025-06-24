import logging
import os
from datetime import datetime

# Ensure the logs directory exists
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)

# Generate a log file name with the current date-time
log_filename = datetime.now().strftime("%Y-%m-%d_%H-%M-%S.log")
log_filepath = os.path.join(log_dir, log_filename)

# Configure the logging settings
logging.basicConfig(
    filename=log_filepath,
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(module)s - %(message)s",
)
logger = logging.getLogger("TaskManagementLogger")
