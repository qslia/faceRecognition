# Image Crawler for Bing Image Search

A simple Python-based web crawler to download images from Bing Image Search results.

## Installation

Install the required dependencies:

```bash
pip install -r crawler_requirements.txt
```

Or install individually:
```bash
pip install requests beautifulsoup4 lxml
```

## Usage

### Basic Usage

Download images for a search query:

```bash
python image_crawler.py --query "obama" --output images/obama --max 30
```

### Examples

**Download Obama images to the data folder:**
```bash
python image_crawler.py -q "obama" -o data/obama -n 50
```

**Download Bill Gates images:**
```bash
python image_crawler.py -q "bill gates" -o data/billgates -n 50
```

**Download with custom delay (more respectful to the server):**
```bash
python image_crawler.py -q "elon musk" -o images/elon -n 20 -d 2.0
```

### Command-line Arguments

- `-q, --query`: Search query (required) - what to search for
- `-o, --output`: Output directory (default: `images/`)
- `-n, --max`: Maximum number of images to download (default: 50)
- `-d, --delay`: Delay between downloads in seconds (default: 1.0)
- `--subfolder`: Create a subfolder within output directory

### Integration with Face Recognition

To use the downloaded images with the face recognition system:

1. Download images for each person:
   ```bash
   python image_crawler.py -q "obama" -o data/obama -n 50
   python image_crawler.py -q "bill gates" -o data/billgates -n 50
   ```

2. Build the face recognition bank:
   ```bash
   python face_recognizer.py build --data-dir data --out face_bank.pt
   ```

3. Run recognition:
   ```bash
   python face_recognizer.py cam --bank face_bank.pt
   ```

## Important Notes

1. **Rate Limiting**: The crawler includes delays between requests to be respectful to Bing's servers. Increase the `--delay` parameter if you encounter issues.

2. **Image Quality**: Downloaded images may vary in quality and relevance. Manual curation is recommended for best face recognition results.

3. **Legal Considerations**: 
   - Respect image copyrights and usage rights
   - Use downloaded images only for personal/educational purposes
   - Some images may have usage restrictions

4. **Reliability**: Web scraping can break if Bing changes their page structure. If the crawler stops working:
   - Try increasing the delay
   - Check your internet connection
   - Bing may have updated their website structure (the script may need updates)

## Troubleshooting

**No images found:**
- Check your internet connection
- Try a different search query
- Bing might be rate limiting your requests (wait a few minutes)
- The page structure may have changed (the script may need updates)

**Failed downloads:**
- Some image URLs may be invalid or expired
- Network timeouts (try increasing the delay)
- Images may have been removed from the source

**Permission errors:**
- Make sure you have write permissions in the output directory
- Try running with appropriate permissions

