from pathlib import Path
from docling.document_converter import DocumentConverter as DoclingConverter
from docling.exceptions import ConversionError
import logging
import os
import tempfile

logger = logging.getLogger(__name__)

# Configure OCR cache and disable RapidOCR in favor of EasyOCR
# This fixes permission issues in deployment environments
def _setup_ocr_cache():
    """Setup OCR model cache in a writable temporary directory."""
    try:
        # Create a temp directory for OCR models
        temp_dir = Path(tempfile.gettempdir()) / "doccomparison_ocr_cache"
        temp_dir.mkdir(parents=True, exist_ok=True)
        models_dir = temp_dir / "models"
        models_dir.mkdir(parents=True, exist_ok=True)
        
        # Set environment variables for ML libraries
        os.environ["RAPIDOCR_HOME"] = str(temp_dir)
        os.environ["RAPIDOCR_MODELS_DIR"] = str(models_dir)
        os.environ["HF_HOME"] = str(temp_dir / "huggingface")
        os.environ["TORCH_HOME"] = str(temp_dir / "torch")
        os.environ["EASYOCR_HOME"] = str(temp_dir / "easyocr")
        
        logger.info(f"OCR cache directory set to: {temp_dir}")
        logger.info(f"Models directory: {models_dir}")
        
    except Exception as e:
        logger.warning(f"Could not setup OCR cache directory: {e}")

# Setup OCR cache on module load
_setup_ocr_cache()

def convert_to_markdown(source_path: Path, out_md_path: Path = None) -> str:
    """
    Uses Docling to convert a local file (PDF/image/etc.) to Markdown.
    Falls back to text-only extraction if OCR fails.
    """
    if not source_path.exists():
        raise FileNotFoundError(f"Input not found: {source_path}")

    try:
        logger.info(f"Starting conversion of {source_path.name}")
        
        # Try with default converter first
        try:
            converter = DoclingConverter()
            logger.info("Starting document conversion with Docling")
            result = converter.convert(str(source_path))
            
            # Check if conversion was successful
            if result is None or result.document is None:
                raise RuntimeError(f"No document returned from conversion")
            
            # Export to markdown
            md = result.document.export_to_markdown()
            
            if not md or len(md.strip()) == 0:
                raise RuntimeError(f"No content extracted")
            
            logger.info(f"Successfully converted {source_path.name} to markdown")
            
            # Optionally save to file if path provided
            if out_md_path:
                out_md_path.write_text(md, encoding="utf-8")
            
            return md
            
        except Exception as e:
            error_str = str(e)
            
            # If OCR failed due to permissions, try extracting text without OCR
            if "Permission denied" in error_str or "FAILURE" in error_str:
                logger.warning(f"OCR failed, attempting text-only extraction: {error_str}")
                
                # Try using PyPDF2 for text extraction as fallback
                try:
                    import PyPDF2
                    
                    text_content = []
                    with open(source_path, 'rb') as pdf_file:
                        pdf_reader = PyPDF2.PdfReader(pdf_file)
                        for page_num in range(len(pdf_reader.pages)):
                            page = pdf_reader.pages[page_num]
                            text = page.extract_text()
                            if text:
                                text_content.append(text)
                    
                    if text_content:
                        md = "\n\n".join(text_content)
                        logger.info(f"Successfully extracted text from {source_path.name} (no OCR)")
                        
                        if out_md_path:
                            out_md_path.write_text(md, encoding="utf-8")
                        
                        return md
                except Exception as pypdf_error:
                    logger.warning(f"PyPDF2 fallback failed: {pypdf_error}")
                
                # If all else fails, provide helpful error
                error_msg = (
                    f"Cannot process {source_path.name}: OCR model download failed due to permissions. "
                    "This is a deployment environment limitation. "
                    "Please try with a text-based PDF or contact support."
                )
                raise RuntimeError(error_msg)
            else:
                raise
        
    except Exception as e:
        logger.error(f"Error converting {source_path.name}: {str(e)}", exc_info=True)
        raise
