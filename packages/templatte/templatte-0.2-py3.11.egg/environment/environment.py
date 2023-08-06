from pathlib import Path
import logging

LOG_LEVEL = logging.DEBUG


def setup_logger():
    logger = logging.getLogger("templatte")  # Set a common logger name
    logger.setLevel(LOG_LEVEL)  # Or any level you need

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Create a console handler
    ch = logging.StreamHandler()
    ch.setLevel(LOG_LEVEL)  # Or any level you need
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    # Optionally add a file handler
    fh = logging.FileHandler("templatte.log")
    fh.setLevel(LOG_LEVEL)  # Or any level you need
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    return logger


def create_folders(folders: list[str]):
    """Create necessary output directories.

    Args:
        folders (list): A list of dictionaries.
    """
    for folder in folders:
        Path(f"{folder}").mkdir(exist_ok=True)
