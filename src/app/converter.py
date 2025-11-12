from pathlib import Path
from docling.document_converter import DocumentConverter as DoclingConverter
from docling.exceptions import ConversionError
import logging
import os
import tempfile

logger = logging.getLogger(__name__)

# Configure RapidOCR to use a writable temp directory for model downloads
# This fixes permission issues in deployment environments
def _setup_ocr_cache():
    """Setup OCR model cache in a writable temporary directory."""
    try:
        # Create a temp directory for OCR models
        temp_dir = Path(tempfile.gettempdir()) / "doccomparison_ocr_cache"
        temp_dir.mkdir(parents=True, exist_ok=True)
        models_dir = temp_dir / "models"
        models_dir.mkdir(parents=True, exist_ok=True)
        
        # Set environment variables for RapidOCR and other ML libraries
        os.environ["RAPIDOCR_HOME"] = str(temp_dir)
        os.environ["RAPIDOCR_MODELS_DIR"] = str(models_dir)
        os.environ["HF_HOME"] = str(temp_dir / "huggingface")
        os.environ["TORCH_HOME"] = str(temp_dir / "torch")
        
        logger.info(f"OCR cache directory set to: {temp_dir}")
        logger.info(f"Models directory: {models_dir}")
        
        # Try to patch RapidOCR's download function to use our temp directory
        try:
            from rapidocr.utils.download_file import download_file as original_download
            
            def patched_download(url, save_path):
                """Patched download that uses our temp directory."""
                # Redirect any venv paths to our temp directory
                if "site-packages/rapidocr" in str(save_path):
                    save_path = str(save_path).replace(
                        "site-packages/rapidocr/models",
                        str(models_dir)
                    )
                    save_path = Path(save_path)
                    save_path.parent.mkdir(parents=True, exist_ok=True)
                
                return original_download(url, save_path)
            
            # Monkey patch the download function
            import rapidocr.utils.download_file
            rapidocr.utils.download_file.download_file = patched_download
            logger.info("RapidOCR download function patched successfully")
        except Exception as e:
            logger.warning(f"Could not patch RapidOCR download: {e}")
            
    except Exception as e:
        logger.warning(f"Could not setup OCR cache directory: {e}")

# Setup OCR cache on module load
_setup_ocr_cache()

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
