#!/bin/bash
# Batch script to download images for multiple people
# Modify the search queries and parameters as needed

echo "============================================"
echo "Image Crawler - Batch Download"
echo "============================================"
echo ""

# Check if required packages are installed
echo "Checking dependencies..."
python -c "import requests, bs4" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "[ERROR] Required packages not found!"
    echo "Please install them first: pip install requests beautifulsoup4 lxml"
    exit 1
fi
echo "[OK] Dependencies installed"
echo ""

# Download Obama images
echo "[1/3] Downloading Obama images..."
python image_crawler.py -q "barack obama" -o data/obama -n 30 -d 1.5
echo ""

# Download Bill Gates images
echo "[2/3] Downloading Bill Gates images..."
python image_crawler.py -q "bill gates" -o data/billgates -n 30 -d 1.5
echo ""

# Add more people here as needed
# echo "[3/3] Downloading [Person Name] images..."
# python image_crawler.py -q "person name" -o data/personname -n 30 -d 1.5
# echo ""

echo "============================================"
echo "Download Complete!"
echo "============================================"
echo ""
echo "Next steps:"
echo "1. Review downloaded images in the data/ folder"
echo "2. Remove any incorrect or low-quality images"
echo "3. Build the face recognition bank:"
echo "   python face_recognizer.py build --data-dir data --out face_bank.pt"
echo ""

