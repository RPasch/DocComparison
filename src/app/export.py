from pathlib import Path
import json

def markdown_to_json(input_file: Path, output_file: Path) -> Path:
    """
    Exports markdown to a JSON array where each element is a line.
    Removes any remaining duplicate lines.
    """
    seen = set()
    unique_lines = []
    
    for ln in input_file.read_text(encoding="utf-8").splitlines():
        line = ln.rstrip("\n")
        if line not in seen:
            seen.add(line)
            unique_lines.append(line)
    
    output_file.write_text(json.dumps(unique_lines, indent=4, ensure_ascii=False), encoding="utf-8")
    return output_file
