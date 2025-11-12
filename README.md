# OCR → Markdown Pipeline

A comprehensive document processing pipeline that converts PDFs and images to markdown, processes them, and compares results.

## Features

- **OCR Conversion**: Convert PDFs, images (PNG, JPG, TIFF, BMP) to markdown using Docling
- **Text Processing**: Remove Arabic characters and deduplicate lines
- **Document Comparison**: Compare two documents for exact matches or differences
- **JSON Export**: Export markdown content as JSON arrays
- **Web UI**: Interactive Streamlit frontend for easy document processing
- **CLI**: Command-line interface for batch processing

## Installation

1. Clone or navigate to the project directory
2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Web Interface (Recommended)

Run the Streamlit app:

```bash
streamlit run app.py
```

Then open your browser to `http://localhost:8501`

**Features:**
- Upload two documents (PDF or image)
- Configure processing options (remove Arabic, deduplicate, compare)
- View markdown output side-by-side
- Compare documents with diff visualization
- Export results as JSON
- Download processed files

### Command Line

Edit `src/main.py` to set your input paths:

```python
SOURCE1 = Path("/path/to/document1.pdf")
SOURCE2 = Path("/path/to/document2.pdf")
```

Then run:

```bash
python src/main.py
```

## Project Structure

```
ocr-md-pipeline/
├── app.py                    # Streamlit web interface
├── requirements.txt          # Python dependencies
├── .env                      # Environment variables (API keys)
├── .env.example              # Example environment file
├── src/
│  ├── main.py               # CLI entry point
│  └── app/
│     ├── __init__.py
│     ├── config.py          # Configuration management
│     ├── converter.py       # Document to markdown conversion
│     ├── text_utils.py      # Text processing utilities
│     ├── compare.py         # Document comparison
│     └── export.py          # Export to JSON/markdown
└── outputs/                 # Generated files (auto-created)
```

## Configuration

### Environment Variables

Create a `.env` file (copy from `.env.example`):

```env
OPENAI_API_KEY=your_key_here
OCR_ENGINE=docling
OUTPUT_DIR=./outputs
LOG_LEVEL=INFO
SIMILARITY_THRESHOLD=0.8
MAX_WORKERS=4
```

### Processing Options

In the Streamlit UI sidebar:
- **Remove Arabic characters**: Filter out Arabic text from OCR output
- **Deduplicate lines**: Remove duplicate lines from markdown
- **Run comparison**: Compare the two documents after processing

## Output Files

All processed files are saved to the `outputs/` directory:

- `doc1_TIMESTAMP.md` - Original markdown from document 1
- `doc1_filtered.md` - After removing Arabic characters
- `doc1_unique.md` - After deduplication
- `doc1_unique.json` - JSON array format

Same pattern for document 2.

## API Keys

### OpenAI API Key

Currently reserved for future enhancements. You can input it in the Streamlit UI sidebar, but it's not actively used yet.

To use it in the future:
1. Get your API key from [OpenAI Platform](https://platform.openai.com/api-keys)
2. Enter it in the Streamlit sidebar
3. It will be available via `get_env("OPENAI_API_KEY")`

## Supported File Formats

- **Documents**: PDF
- **Images**: PNG, JPG, JPEG, TIFF, BMP

## Dependencies

- **docling**: Document OCR and conversion
- **python-dotenv**: Environment variable management
- **rich**: Terminal formatting
- **streamlit**: Web interface

## Troubleshooting

### Docling not installed
```bash
pip install docling
```

### File not found error
Ensure the file path is correct and the file exists.

### Arabic character removal not working
Check that the input markdown contains Arabic characters in the expected Unicode ranges.

## Future Enhancements

- OpenAI API integration for advanced text processing
- Anthropic Claude integration
- Batch processing for multiple document pairs
- Advanced similarity metrics
- Custom text processing pipelines
- Export to additional formats (PDF, DOCX, HTML)

## License

MIT

## Support

For issues or questions, check the output logs in the `outputs/` directory.
