from pathlib import Path
from docling.document_converter import DocumentConverter as DoclingConverter
from docling.pipeline_options import StandardPdfPipelineOptions
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

def convert_to_markdown(source_path: Path, out_md_path: Path) -> Path:
    """
    Uses Docling to convert a local file (PDF/image/etc.) to Markdown.
    Uses EasyOCR for better deployment compatibility.
    """
    if not source_path.exists():
        raise FileNotFoundError(f"Input not found: {source_path}")

    try:
        logger.info(f"Starting conversion of {source_path.name}")
        
        # Use EasyOCR instead of RapidOCR for better deployment compatibility
        try:
            pipeline_options = StandardPdfPipelineOptions(
                do_ocr=True,
                ocr_engine="easyocr"  # Use EasyOCR instead of RapidOCR
            )
            converter = DoclingConverter(pipeline_options=pipeline_options)
            logger.info("Using EasyOCR engine for conversion")
        except Exception as e:
            logger.warning(f"Could not configure EasyOCR, using default: {e}")
            # Fallback to default converter
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
