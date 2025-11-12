from pathlib import Path

def compare_files(file1: Path, file2: Path) -> bool:
    """
    Exact content comparison (strict).
    """
    c1 = file1.read_text(encoding="utf-8")
    c2 = file2.read_text(encoding="utf-8")
    same = (c1 == c2)
    return same
