import os
from pathlib import Path


DB_PATH = Path(os.getenv("HOME"), ".config", "kaam", "sqlite.db")
VERSION = "0.0.3"
