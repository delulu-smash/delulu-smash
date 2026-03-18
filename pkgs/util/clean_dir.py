from __future__ import annotations

from pathlib import Path

from util.logging import logger


def remove_files(filename: str, target_directory: str, dry_run: bool) -> None:
    """
    Auto-generated via Google Gemini
    recursively delete specific files using pathlib.
    """
    count: int = 0
    base_path: Path = Path(target_directory)

    # Validate directory existence
    if not base_path.is_dir():
        logger.info(f"Error: '{target_directory}' is not a valid directory.")
        return

    logger.info(f"Searching for '{filename}' in: {base_path.resolve()}")
    if dry_run:
        logger.info("--- RUNNING IN DRY-RUN MODE (No files will be deleted) ---\n")

    # Use rglob to recursively find all files matching the name
    for file_path in base_path.rglob(filename):
        if file_path.is_file():
            if dry_run:
                logger.info(f"[FOUND] {file_path}")
                count += 1
            else:
                try:
                    file_path.unlink()
                    logger.info(f"DELETED: {file_path}")
                    count += 1
                except Exception as e:
                    logger.info(f"ERROR: Could not delete {file_path}. Reason: {e}")

    # Summary of actions
    status: str = "would be" if dry_run else "were"
    logger.info(f"\nTask complete. {count} occurrence(s) of '{filename}' {status} removed.")
