from pathlib import Path
from docling.document_converter import DocumentConverter as DoclingConverter

def convert_to_markdown(source_path: Path, out_md_path: Path) -> Path:
    """
    Uses Docling to convert a local file (PDF/image/etc.) to Markdown.
    """
    if not source_path.exists():
        raise FileNotFoundError(f"Input not found: {source_path}")

    converter = DoclingConverter()
    result = converter.convert(str(source_path))
    md = result.document.export_to_markdown()

    out_md_path.write_text(md, encoding="utf-8")
    return out_md_path
