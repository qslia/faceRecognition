# Quick Start Guide - Image Crawler

## Installation

First, install the required dependencies:

```bash
pip install requests beautifulsoup4 lxml
```

## Basic Usage

### 1. Download Obama Images

```bash
python image_crawler.py -q "obama" -o images/obama -n 30
```

This will:
- Search Bing for "obama" images
- Download up to 30 images
- Save them to `images/obama/` folder

### 2. Download to Data Folder (for Face Recognition)

```bash
python image_crawler.py -q "barack obama" -o data/obama -n 50
```

### 3. Other Examples

```bash
# Bill Gates images
python image_crawler.py -q "bill gates" -o data/billgates -n 50

# Elon Musk images with slower downloads (2 second delay)
python image_crawler.py -q "elon musk" -o images/elon -n 20 -d 2.0

# Any other person
python image_crawler.py -q "your search term" -o images/folder_name -n 25
```

## Full Workflow with Face Recognition

### Step 1: Download Training Images

Download images for each person you want to recognize:

```bash
# Download Obama images
python image_crawler.py -q "barack obama portrait" -o data/obama -n 50

# Download Bill Gates images  
python image_crawler.py -q "bill gates portrait" -o data/billgates -n 50

# Add more people as needed
python image_crawler.py -q "elon musk portrait" -o data/elonmusk -n 50
```

### Step 2: Build Face Recognition Bank

After downloading images, build the face recognition database:

```bash
python face_recognizer.py build --data-dir data --out face_bank.pt
```

### Step 3: Test on Single Image

Test recognition on a single image:

```bash
python face_recognizer.py infer --img test_image.jpg --bank face_bank.pt
```

### Step 4: Run Live Recognition

Use your webcam for live face recognition:

```bash
python face_recognizer.py cam --bank face_bank.pt
```

## Command-Line Options

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--query` | `-q` | Search term (required) | - |
| `--output` | `-o` | Output directory | `images/` |
| `--max` | `-n` | Max number of images | `50` |
| `--delay` | `-d` | Delay between downloads (seconds) | `1.0` |
| `--subfolder` | - | Subfolder within output directory | None |

## Tips

1. **Better Results**: Use specific search terms like "person name portrait" or "person name face close-up"

2. **Avoid Rate Limiting**: 
   - Use delays between downloads (`-d 2.0` for 2 seconds)
   - Don't download too many images at once
   - If you get blocked, wait a few minutes before trying again

3. **Image Quality**: 
   - After downloading, manually review images
   - Remove low-quality or incorrect images
   - Keep only clear face shots for best recognition results

4. **Legal Compliance**:
   - Use images for personal/educational purposes only
   - Respect copyright and usage rights
   - Some images may have restrictions

## Troubleshooting

**Problem**: No images downloaded
- Check internet connection
- Try different search terms
- Increase delay with `-d 2.0` or higher
- Wait a few minutes if rate limited

**Problem**: Some downloads fail
- This is normal; not all URLs work
- The script will continue with other images
- Try running again to get more images

**Problem**: "Permission denied" error
- Make sure you have write access to the output directory
- Try a different output location

## Advanced Usage

### Download Multiple Categories

Create a batch script to download multiple people:

**Windows (batch.cmd):**
```batch
@echo off
python image_crawler.py -q "barack obama" -o data/obama -n 50 -d 1.5
python image_crawler.py -q "bill gates" -o data/billgates -n 50 -d 1.5
python image_crawler.py -q "elon musk" -o data/elonmusk -n 50 -d 1.5
echo Done!
```

**Linux/Mac (batch.sh):**
```bash
#!/bin/bash
python image_crawler.py -q "barack obama" -o data/obama -n 50 -d 1.5
python image_crawler.py -q "bill gates" -o data/billgates -n 50 -d 1.5
python image_crawler.py -q "elon musk" -o data/elonmusk -n 50 -d 1.5
echo "Done!"
```

## Next Steps

1. Download images for people you want to recognize
2. Review and clean up downloaded images
3. Build the face recognition bank
4. Test and enjoy!

For more details, see `CRAWLER_README.md`.

