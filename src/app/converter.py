from pathlib import Path
from docling.document_converter import DocumentConverter as DoclingConverter
from docling.pipeline_options import PdfPipelineOptions
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
        
        # Try with default settings first
        try:
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
            # If default conversion fails, try with OCR disabled (for text-based PDFs)
            if "Permission denied" in str(e) or "FAILURE" in str(e):
                logger.warning(f"Default conversion failed, trying without OCR: {str(e)}")
                
                # Create pipeline options with OCR disabled
                pipeline_options = PdfPipelineOptions(
                    do_ocr=False,
                    do_table_structure=True
                )
                converter = DoclingConverter(pipeline_options=pipeline_options)
                result = converter.convert(str(source_path))
                
                if result is None or result.document is None:
                    raise RuntimeError(f"Conversion failed for: {source_path.name} - No document returned")
                
                md = result.document.export_to_markdown()
                
                if not md or len(md.strip()) == 0:
                    raise RuntimeError(f"No content extracted from {source_path.name}")
                
                out_md_path.write_text(md, encoding="utf-8")
                logger.info(f"Successfully converted {source_path.name} to markdown (without OCR)")
                return out_md_path
            else:
                raise
        
    except Exception as e:
        logger.error(f"Error converting {source_path.name}: {str(e)}", exc_info=True)
        raise
