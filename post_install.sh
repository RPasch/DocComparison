#!/bin/bash
# Post-install script to remove RapidOCR and ensure EasyOCR is used
# This fixes permission issues in deployment environments

echo "Removing RapidOCR to avoid permission issues..."
pip uninstall -y rapidocr 2>/dev/null || true

echo "Ensuring EasyOCR is installed..."
pip install easyocr>=1.7.0

echo "Post-install setup complete!"
