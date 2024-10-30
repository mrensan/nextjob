import logging
import sys
from pathlib import Path
import platform


def get_log_file():
    """Get the log file."""
    if platform.system() == "Windows":
        log_dir = Path.home() / "AppData/Local/NextJob"
    elif platform.system() == "Darwin":  # macOS
        log_dir = Path.home() / "Library/Logs/NextJob"
    else:  # Linux and other systems
        log_dir = Path.home() / ".nextjob/logs"

    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir / "nextjob.log"


log_file = get_log_file()
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG,
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(log_file, mode="a", encoding="utf-8")
    ]
)


def get_data_file():
    """Get the data file."""
    if platform.system() == "Windows":
        data_dir = Path.home() / "AppData/Local/NextJob"
    elif platform.system() == "Darwin":
        data_dir = Path.home() / "Library/Application Support/NextJob"
    else:  # Linux and other systems
        data_dir = Path.home() / ".nextjob"

    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir / "db.json"


def flatten_dict(d, parent_key=''):
    """Flatten a dictionary."""
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}.{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key).items())
        elif isinstance(v, list):
            for index, item in enumerate(v):
                if isinstance(item, dict):
                    items.extend(flatten_dict(item, f"{new_key}[{index}]").items())
                else:
                    items.append((f"{new_key}[{index}]", str(item)))
        else:
            items.append((new_key, str(v)))
    return dict(items)
