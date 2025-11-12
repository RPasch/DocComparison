from pathlib import Path
from docling.document_converter import DocumentConverter as DoclingConverter
import logging

logger = logging.getLogger(__name__)

def convert_to_markdown(source_path: Path, out_md_path: Path) -> Path:
    """
    Uses Docling to convert a local file (PDF/image/etc.) to Markdown.
    """
    if not source_path.exists():
        raise FileNotFoundError(f"Input not found: {source_path}")

    try:
        logger.info(f"Starting conversion of {source_path.name}")
        converter = DoclingConverter()
        result = converter.convert(str(source_path))
        
        # Check if conversion was successful
        if result is None or result.document is None:
            error_msg = f"Conversion failed for: {source_path.name} - No document returned"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
        
        # Export to markdown
        md = result.document.export_to_markdown()
        
        if not md or len(md.strip()) == 0:
            raise RuntimeError(f"No content extracted from {source_path.name}")
        
        out_md_path.write_text(md, encoding="utf-8")
        logger.info(f"Successfully converted {source_path.name} to markdown")
        return out_md_path
        
    except Exception as e:
        logger.error(f"Error converting {source_path.name}: {str(e)}", exc_info=True)
        raise
