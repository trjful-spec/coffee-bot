from pathlib import Path
from datetime import datetime
import subprocess


VERSION = "1.0.0"


def get_commit_hash() -> str:
    try:
        return (
            subprocess.check_output(
                ["git", "rev-parse", "--short", "HEAD"],
                stderr=subprocess.DEVNULL,
            )
            .decode()
            .strip()
        )
    except (subprocess.SubprocessError, FileNotFoundError):
        return "unknown"


def get_full_version() -> str:
    return f"{VERSION} ({get_commit_hash()})"


def get_started_at() -> str:
    return datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )


def write_version_file() -> None:
    version_file = Path(".version")

    version_file.write_text(
        (
            "Coffee Bot\n\n"
            f"Version: {VERSION}\n"
            f"Commit: {get_commit_hash()}\n"
            f"Started: {get_started_at()}\n"
        ),
        encoding="utf-8",
    )