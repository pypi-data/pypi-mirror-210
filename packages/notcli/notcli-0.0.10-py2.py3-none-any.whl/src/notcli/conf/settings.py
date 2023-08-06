from pathlib import Path
from os import path as os_path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
TTY_ECHO_PATH = BASE_DIR / "tty"
STATIC_DIR = os_path.join(BASE_DIR, "notcli", "static")
