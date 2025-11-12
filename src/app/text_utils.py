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
    Also removes repeated patterns within table cells.
    """
    seen = set()
    out_lines = []
    
    for line in input_file.read_text(encoding="utf-8").splitlines(keepends=False):
        # For table rows, remove repeated cell content
        if line.startswith("|"):
            # Split by pipe, remove duplicates within cells, rejoin
            cells = line.split("|")
            deduplicated_cells = []
            prev_cell = None
            
            for cell in cells:
                cell_stripped = cell.strip()
                # Only add if it's different from previous cell or empty
                if cell_stripped != prev_cell or cell_stripped == "":
                    deduplicated_cells.append(cell)
                    prev_cell = cell_stripped
            
            line = "|".join(deduplicated_cells)
        
        # Remove duplicate lines
        if line not in seen:
            seen.add(line)
            out_lines.append(line)
    
    output_file.write_text("\n".join(out_lines) + "\n", encoding="utf-8")
    return output_file
