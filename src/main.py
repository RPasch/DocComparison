"""Main entry point for OCR MD Pipeline."""

import logging
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from app.config import get_config
from app.converter import DocumentConverter
from app.compare import DocumentComparator
from app.export import Exporter


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main application entry point."""
    logger.info("Starting OCR MD Pipeline")

    try:
        # Load configuration
        config = get_config()
        logger.info(f"Configuration loaded. OCR Engine: {config.ocr_engine}")

        # Initialize components
        converter = DocumentConverter(config)
        comparator = DocumentComparator(config)
        exporter = Exporter(config.output_dir)

        logger.info("All components initialized successfully")

        # Example usage (uncomment to use):
        # doc1_path = "path/to/document1.pdf"
        # doc2_path = "path/to/document2.pdf"
        #
        # md1 = converter.convert_to_markdown(doc1_path)
        # md2 = converter.convert_to_markdown(doc2_path)
        #
        # comparison_result = comparator.compare_documents(md1, md2)
        # exporter.export_to_json(comparison_result)

    except Exception as e:
        logger.error(f"Application error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
