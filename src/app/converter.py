from pathlib import Path
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
    Converts PDF/image to Markdown using pdf2image + Tesseract OCR.
    Avoids RapidOCR permission issues by using direct OCR approach.
    """
    if not source_path.exists():
        raise FileNotFoundError(f"Input not found: {source_path}")

    if not _tesseract_available:
        raise RuntimeError("Tesseract OCR is not installed. Cannot process scanned documents.")

    try:
        logger.info(f"Starting conversion of {source_path.name}")
        
        from pdf2image import convert_from_path
        import pytesseract
        from PIL import Image
        
        # Convert PDF to images
        logger.info(f"Converting PDF to images...")
        images = convert_from_path(str(source_path), dpi=300)
        logger.info(f"Converted {len(images)} pages")
        
        # Extract text from each image using Tesseract
        all_text = []
        for page_num, image in enumerate(images, 1):
            logger.info(f"OCR processing page {page_num}/{len(images)}")
            text = pytesseract.image_to_string(image)
            if text.strip():
                all_text.append(f"## Page {page_num}\n\n{text}")
        
        if not all_text:
            raise RuntimeError(f"No text extracted from {source_path.name}")
        
        md = "\n\n---\n\n".join(all_text)
        logger.info(f"Successfully converted {source_path.name} to markdown")
        
        # Optionally save to file if path provided
        if out_md_path:
            out_md_path.write_text(md, encoding="utf-8")
        
        return md
        
    except Exception as e:
        logger.error(f"Error converting {source_path.name}: {str(e)}", exc_info=True)
        raise
