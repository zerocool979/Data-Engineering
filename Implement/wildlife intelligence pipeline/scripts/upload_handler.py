import os
import shutil
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "uploads")


def save_uploaded_file(uploaded_file) -> str:
    """
    Save an uploaded Streamlit file object to the uploads directory.
    Returns the path to the saved file.
    """
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    if not uploaded_file.name.endswith(".csv"):
        raise ValueError("Invalid file format. Only CSV files are accepted.")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"uploaded_{timestamp}.csv"
    dest_path = os.path.join(UPLOAD_DIR, filename)

    with open(dest_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    logger.info(f"File saved to {dest_path}")
    return dest_path


def get_latest_upload() -> str | None:
    """Return the path of the most recently uploaded file."""
    if not os.path.exists(UPLOAD_DIR):
        return None

    files = [
        os.path.join(UPLOAD_DIR, f)
        for f in os.listdir(UPLOAD_DIR)
        if f.endswith(".csv")
    ]
    if not files:
        return None

    return max(files, key=os.path.getmtime)
