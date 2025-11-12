from pathlib import Path
from docling.document_converter import DocumentConverter as DoclingConverter
from docling.exceptions import ConversionError
import logging
import os
import tempfile
import subprocess

logger = logging.getLogger(__name__)

# Check if Tesseract is installed
def _check_tesseract():
    """Check if Tesseract OCR is available."""
    try:
        result = subprocess.run(['tesseract', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            logger.info("Tesseract OCR is available")
            return True
    except FileNotFoundError:
        logger.warning("Tesseract OCR not found in system PATH")
    return False

_tesseract_available = _check_tesseract()

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
    Uses Tesseract OCR for scanned documents.
    """
    if not source_path.exists():
        raise FileNotFoundError(f"Input not found: {source_path}")

    try:
        logger.info(f"Starting conversion of {source_path.name}")
        
        # Set Tesseract as preferred OCR engine if available
        if _tesseract_available:
            os.environ["DOCLING_OCR_ENGINE"] = "tesseract"
            logger.info("Using Tesseract OCR engine")
        else:
            logger.warning("Tesseract not available, using default OCR engine")
        
        converter = DoclingConverter()
        logger.info(f"Starting document conversion with Docling")
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
        logger.error(f"Error converting {source_path.name}: {str(e)}", exc_info=True)
        raise
