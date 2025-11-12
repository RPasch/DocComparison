from pathlib import Path
import re

# Expanded Arabic Unicode ranges (basic + supplement + extended + presentation forms)
_ARABIC_RANGES_PATTERN = (
    r"[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]+"
)

def remove_arabic_chars(input_file: Path, output_file: Path) -> Path:
    """
    Removes Arabic characters for readability post-OCR (optional step).
    """
    content = input_file.read_text(encoding="utf-8")
    filtered = re.sub(_ARABIC_RANGES_PATTERN, "", content)
    output_file.write_text(filtered, encoding="utf-8")
    return output_file

def remove_duplicate_lines(input_file: Path, output_file: Path) -> Path:
    """
    Deduplicates lines while preserving first occurrence order.
    """
    seen = set()
    out_lines = []
    for line in input_file.read_text(encoding="utf-8").splitlines(keepends=False):
        if line not in seen:
            seen.add(line)
            out_lines.append(line)
    
    output_file.write_text("\n".join(out_lines) + "\n", encoding="utf-8")
    return output_file

def remove_duplicate_lines_in_memory(content: str) -> str:
    """
    Deduplicates lines in memory while preserving first occurrence order.
    """
    seen = set()
    out_lines = []
    for line in content.splitlines(keepends=False):
        if line not in seen:
            seen.add(line)
            out_lines.append(line)
    return "\n".join(out_lines)

def remove_arabic_chars_in_memory(content: str) -> str:
    """
    Removes Arabic characters from content in memory.
    """
    return re.sub(_ARABIC_RANGES_PATTERN, "", content)
