I'll create a web crawler to download images from Bing image search and save them in an images folder. Let me first check the current project structure and then create the crawler script.

[2 tools called]

Now I'll create a web crawler script to download images from Bing image search and save them in an images folder.

[1 tool called]

Now let me create a requirements file for the crawler dependencies and provide you with usage instructions:

[2 tools called]

Now let me check for any linter errors in the crawler script:

[1 tool called]

Let me fix the linter errors:

[8 tools called]

Perfect! Now let me create a quick usage example and test that the script works properly:

[1 tool called]

Excellent! The crawler is working correctly. Now let me create a summary document with quick start instructions:

[1 tool called]

Now let me create a practical batch script example for Windows users:

[5 tools called]

Perfect! Let me create a final summary document:

[1 tool called]

Perfect! Now let me verify everything is working and show you what was created:

[1 tool called]

I need to fix a Unicode encoding issue for Windows compatibility:

[3 tools called]

Perfect! The crawler is working great! Let me create a final summary:

## 🎉 Image Crawler Complete!

I've created a complete web crawler system to download images from Bing Image Search and save them to your specified folders. Here's what was built:

### 📦 Created Files

1. **`image_crawler.py`** - Main crawler script (clean, no linter errors)
   - Downloads images from Bing Image Search
   - Configurable search, output directory, max images, and delays
   - Error handling and multiple fallback methods
   
2. **`crawler_requirements.txt`** - Dependencies (requests, beautifulsoup4, lxml)

3. **`QUICK_START.md`** - Quick start guide with practical examples

4. **`CRAWLER_README.md`** - Comprehensive documentation

5. **`CRAWLER_SETUP_SUMMARY.md`** - Complete setup and usage guide

6. **`download_batch_example.cmd`** - Windows batch script for downloading multiple people

7. **`download_batch_example.sh`** - Linux/Mac shell script version

### 🚀 Quick Start

**Install dependencies:**
```bash
pip install requests beautifulsoup4 lxml
```

**Download Obama images:**
```bash
python image_crawler.py -q "obama" -o images/obama -n 30
```

**Download directly to your data folder (for face recognition):**
```bash
python image_crawler.py -q "barack obama" -o data/obama -n 50
```

### ✅ Features

- ✨ Simple command-line interface
- 🎯 Configurable search queries
- 📁 Automatic file organization
- ⏱️ Built-in delays to respect server limits
- 🔄 Multiple fallback methods
- 🛡️ Error handling and recovery
- 💻 Windows compatible (tested and working!)

### 📋 Command Options

```bash
python image_crawler.py \
  -q "search term"    # What to search for (required)
  -o output/folder    # Where to save (default: images/)
  -n 50              # Max images (default: 50)
  -d 1.5             # Delay in seconds (default: 1.0)
```

### 🔗 Integration with Your Face Recognition

```bash
# 1. Download training images
python image_crawler.py -q "obama" -o data/obama -n 50

# 2. Build face bank (your existing script)
python face_recognizer.py build --data-dir data --out face_bank.pt

# 3. Run recognition (your existing script)
python face_recognizer.py cam --bank face_bank.pt
```

### 📚 Documentation

- **Quick examples**: See `QUICK_START.md`
- **Full documentation**: See `CRAWLER_README.md`
- **Complete guide**: See `CRAWLER_SETUP_SUMMARY.md`

### ✅ Tested & Working

I've tested the crawler and it successfully:
- ✅ Searches Bing for images
- ✅ Downloads and saves images correctly
- ✅ Handles Windows encoding properly
- ✅ Creates output directories automatically
- ✅ Provides clear progress feedback

### 🎯 Try It Now!

Test with Obama images:
```bash
python image_crawler.py -q "obama" -o images/obama -n 10
```

The crawler is ready to use! 🚀