from pathlib import Path


def collect_csv_files(directory: Path) -> list[Path]:
    """
    Collect all CSV files from a directory.

    Args:
        directory: Path to the directory to search

    Returns:
        List of CSV file paths
    """
    if not directory.exists():
        print(f"Directory {directory} does not exist")
        return []
    return list(directory.glob("*.csv"))
