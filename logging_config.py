
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

# Create a logs directory
LOG_DIR = Path(__file__).resolve().parent / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

LOG_FILE = LOG_DIR / "app.log"

# Define the log format
LOG_FORMAT = (
    "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)

formatter = logging.Formatter(LOG_FORMAT)

# Display logs in the terminal
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

# Save logs to a file
file_handler = RotatingFileHandler(
    LOG_FILE,
    maxBytes=1_000_000,
    backupCount=3,
    encoding="utf-8",
)
file_handler.setFormatter(formatter)

# Configure the application logger
logger = logging.getLogger("ai_job_automation")
logger.setLevel(logging.INFO)

logger.handlers.clear()
logger.addHandler(console_handler)
logger.addHandler(file_handler)

logger.propagate = False
