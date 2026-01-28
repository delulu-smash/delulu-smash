# ---------------------------------------------------------------------------
# Auto-generated via Google Gemini
# Description: A CLI tool to recursively delete specific files using pathlib.
#
# Example CLI Commands:
#   1. Clean current directory:          uv run scripts/clean_dir.py .DS_Store
#   2. Clean a specific path:            uv run scripts/clean_dir.py .DS_Store /Users/name
#   3. Safety check (Dry Run):           uv run scripts/clean_dir.py Thumbs.db --dry-run
#   4. Delete specific named file:       uv run scripts/clean_dir.py temp_log.txt
# ---------------------------------------------------------------------------
from __future__ import annotations

import argparse
from pathlib import Path


def remove_files(filename: str, target_directory: str, dry_run: bool = False) -> None:
    count: int = 0
    base_path: Path = Path(target_directory)

    # Validate directory existence
    if not base_path.is_dir():
        print(f"Error: '{target_directory}' is not a valid directory.")
        return

    print(f"Searching for '{filename}' in: {base_path.resolve()}")
    if dry_run:
        print("--- RUNNING IN DRY-RUN MODE (No files will be deleted) ---\n")

    # Use rglob to recursively find all files matching the name
    for file_path in base_path.rglob(filename):
        if file_path.is_file():
            if dry_run:
                print(f"[FOUND] {file_path}")
                count += 1
            else:
                try:
                    file_path.unlink()
                    print(f"DELETED: {file_path}")
                    count += 1
                except Exception as e:
                    print(f"ERROR: Could not delete {file_path}. Reason: {e}")

    # Summary of actions
    status: str = "would be" if dry_run else "were"
    print(f"\nTask complete. {count} occurrence(s) of '{filename}' {status} removed.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Recursively delete a specific file by name from a directory tree.")

    # Required: The name of the file to delete
    parser.add_argument("filename", type=str, help="The exact name of the file you want to remove (e.g., .DS_Store)")

    # Optional: The directory path (defaults to current directory '.')
    parser.add_argument(
        "path", type=str, nargs="?", default=".", help="The root directory to search (default: current directory)"
    )

    # Optional flag for dry run
    parser.add_argument("--dry-run", action="store_true", help="Search and list matching files without deleting them")

    args = parser.parse_args()
    remove_files(args.filename, args.path, args.dry_run)


if __name__ == "__main__":
    main()
