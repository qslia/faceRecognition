import requests
from bs4 import BeautifulSoup
import os
import time
import argparse
from pathlib import Path
from urllib.parse import urlparse
import re


class BingImageCrawler:
    """
    A simple web crawler to download images from Bing Image Search.
    """

    def __init__(self, output_dir="images", max_images=50, delay=1.0):
        """
        Initialize the crawler.

        Args:
            output_dir: Directory to save downloaded images
            max_images: Maximum number of images to download
            delay: Delay between requests in seconds (to be respectful)
        """
        self.output_dir = Path(output_dir)
        self.max_images = max_images
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/91.0.4472.124 Safari/537.36"
                )
            }
        )

    def search_bing_images(self, query):
        """
        Search Bing for images and return image URLs.

        Args:
            query: Search query string

        Returns:
            List of image URLs
        """
        search_url = (
            f"https://www.bing.com/images/search?" f"q={query}&form=HDRSC3&first=1"
        )

        try:
            response = self.session.get(search_url, timeout=10)
            response.raise_for_status()

            # Parse the page
            soup = BeautifulSoup(response.text, "html.parser")

            # Method 1: Look for image URLs in the page source
            image_urls = []

            # Try to find JSON data with image URLs
            scripts = soup.find_all("script")
            for script in scripts:
                if script.string and "murl" in script.string:
                    # Extract URLs from JSON-like structures
                    matches = re.findall(r'"murl":"([^"]+)"', script.string)
                    image_urls.extend(matches)

                if script.string and "mediaurl" in script.string.lower():
                    matches = re.findall(
                        r'"mediaurl":"([^"]+)"', script.string, re.IGNORECASE
                    )
                    image_urls.extend(matches)

            # Method 2: Look for img tags with data attributes
            for img in soup.find_all("img", class_="mimg"):
                if img.get("src"):
                    image_urls.append(img["src"])
                if img.get("data-src"):
                    image_urls.append(img["data-src"])

            # Method 3: Look for any img tags with reasonable URLs
            for img in soup.find_all("img"):
                src = img.get("src") or img.get("data-src")
                if src and src.startswith("http"):
                    if "logo" not in src.lower():
                        exts = [".jpg", ".jpeg", ".png", ".webp"]
                        if any(ext in src.lower() for ext in exts):
                            image_urls.append(src)

            # Clean and deduplicate URLs
            image_urls = list(
                set([url for url in image_urls if url.startswith("http")])
            )

            print(f"Found {len(image_urls)} image URLs")
            return image_urls[: self.max_images]

        except Exception as e:
            print(f"Error searching Bing: {e}")
            return []

    def download_image(self, url, save_path):
        """
        Download a single image from URL.

        Args:
            url: Image URL
            save_path: Path to save the image

        Returns:
            True if successful, False otherwise
        """
        try:
            response = self.session.get(url, timeout=10, stream=True)
            response.raise_for_status()

            # Check if response is actually an image
            content_type = response.headers.get("content-type", "")
            if "image" not in content_type.lower():
                print(f"Skipping non-image content: {content_type}")
                return False

            # Save the image
            with open(save_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            return True

        except Exception as e:
            print(f"Error downloading {url}: {e}")
            return False

    def crawl(self, query, subfolder=None):
        """
        Main crawl function to search and download images.

        Args:
            query: Search query
            subfolder: Optional subfolder name within output_dir
        """
        # Create output directory
        if subfolder:
            output_path = self.output_dir / subfolder
        else:
            output_path = self.output_dir

        output_path.mkdir(parents=True, exist_ok=True)

        print(f"Searching Bing for: {query}")
        print(f"Output directory: {output_path}")

        # Search for images
        image_urls = self.search_bing_images(query)

        if not image_urls:
            print("No images found. This might be due to:")
            print("1. Bing's page structure has changed")
            print("2. Rate limiting or blocking")
            print("3. Network issues")
            print("\nTrying alternative method...")

            # Alternative: Use Bing Image Search API endpoint (limited)
            image_urls = self.search_bing_api(query)

        if not image_urls:
            msg = (
                "Could not retrieve images. "
                "Please try again later or use manual download."
            )
            print(msg)
            return

        # Download images
        downloaded = 0
        for i, url in enumerate(image_urls[: self.max_images]):
            # Determine file extension
            parsed = urlparse(url)
            ext = os.path.splitext(parsed.path)[1]
            valid_exts = [".jpg", ".jpeg", ".png", ".webp", ".bmp"]
            if not ext or ext not in valid_exts:
                ext = ".jpg"

            filename = f"{query.replace(' ', '_')}_{i+1:03d}{ext}"
            save_path = output_path / filename

            print(f"Downloading {i+1}/{len(image_urls)}: {filename}")

            if self.download_image(url, save_path):
                downloaded += 1
                print(f"  [OK] Saved: {save_path}")
            else:
                print("  [FAILED]")

            # Be respectful with delays
            if i < len(image_urls) - 1:
                time.sleep(self.delay)

        output_msg = (
            f"\nCompleted! Downloaded {downloaded}/{len(image_urls)} "
            f"images to {output_path}"
        )
        print(output_msg)

    def search_bing_api(self, query):
        """
        Alternative method using Bing's JSON API endpoint.
        """
        try:
            api_url = (
                f"https://www.bing.com/images/async?q={query}"
                f"&first=1&count={self.max_images}&mmasync=1"
            )
            response = self.session.get(api_url, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")
            image_urls = []

            # Extract from data attributes
            for img in soup.find_all("img"):
                for attr in ["src", "data-src", "data-src-hq"]:
                    url = img.get(attr)
                    if url and url.startswith("http"):
                        image_urls.append(url)

            return list(set(image_urls))[: self.max_images]

        except Exception as e:
            print(f"API method failed: {e}")
            return []


def main():
    parser = argparse.ArgumentParser(
        description="Download images from Bing Image Search",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python image_crawler.py --query "obama" --output images/obama --max 30
  python image_crawler.py -q "bill gates" -o data/billgates --max 50
  python image_crawler.py -q "elon musk" -o images/elon -n 20
        """,
    )

    parser.add_argument(
        "-q",
        "--query",
        type=str,
        required=True,
        help='Search query (e.g., "obama", "bill gates")',
    )

    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default="images",
        help="Output directory to save images (default: images/)",
    )

    parser.add_argument(
        "-n",
        "--max",
        type=int,
        default=50,
        help="Maximum number of images to download (default: 50)",
    )

    parser.add_argument(
        "-d",
        "--delay",
        type=float,
        default=1.0,
        help="Delay between downloads in seconds (default: 1.0)",
    )

    parser.add_argument(
        "--subfolder",
        type=str,
        default=None,
        help=("Create a subfolder with this name " "(useful for organizing by person)"),
    )

    args = parser.parse_args()

    # Create crawler instance
    crawler = BingImageCrawler(
        output_dir=args.output, max_images=args.max, delay=args.delay
    )

    # Run the crawl
    crawler.crawl(args.query, args.subfolder)


if __name__ == "__main__":
    main()
