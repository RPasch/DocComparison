#!/bin/bash
# Post-install script to remove RapidOCR and ensure EasyOCR is used
# This fixes permission issues in deployment environments

echo "Removing RapidOCR to avoid permission issues..."
pip uninstall -y rapidocr rapidocr-onnxruntime 2>/dev/null || true

echo "Ensuring EasyOCR is installed..."
pip install easyocr>=1.7.0

echo "Verifying RapidOCR is removed..."
python -c "import sys; sys.exit(0 if __import__('importlib.util').util.find_spec('rapidocr') is None else 1)" && echo "✓ RapidOCR successfully removed" || echo "⚠ RapidOCR still present"

echo "Post-install setup complete!"
