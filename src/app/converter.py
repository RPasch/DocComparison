from pathlib import Path
from docling.document_converter import DocumentConverter as DoclingConverter
from docling.exceptions import ConversionError
import logging
import os

logger = logging.getLogger(__name__)

def convert_to_markdown(source_path: Path, out_md_path: Path) -> Path:
    """
    Uses Docling to convert a local file (PDF/image/etc.) to Markdown.
    Handles permission issues with OCR model downloads.
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
        
    except ConversionError as e:
        # Handle Docling conversion errors
        error_str = str(e)
        logger.error(f"Docling conversion error for {source_path.name}: {error_str}")
        
        if "Permission denied" in error_str or "FAILURE" in error_str:
            error_msg = (
                f"Cannot process {source_path.name}: OCR model download failed due to permissions. "
                "This is a deployment environment limitation. "
                "Please try with a text-based PDF or contact support."
            )
            raise RuntimeError(error_msg)
        else:
            raise RuntimeError(f"Conversion failed for {source_path.name}: {error_str}")
        
    except Exception as e:
        logger.error(f"Error converting {source_path.name}: {str(e)}", exc_info=True)
        raise
