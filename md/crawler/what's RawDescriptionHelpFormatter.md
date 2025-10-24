[1 tool called]

This is **`argparse.RawDescriptionHelpFormatter`** - a formatter class for the command-line argument parser.

## What it does:

**`formatter_class=argparse.RawDescriptionHelpFormatter`** tells argparse to preserve the formatting of the help text exactly as written, including:
- Line breaks
- Indentation
- Whitespace

## Why it's used here:

Look at the `epilog` parameter (lines 241-246) - it contains formatted example commands:

```python
epilog="""
Examples:
  python image_crawler.py --query "obama" --output images/obama --max 30
  python image_crawler.py -q "bill gates" -o data/billgates --max 50
  python image_crawler.py -q "elon musk" -o images/elon -n 20
        """
```

### Without `RawDescriptionHelpFormatter`:
The default formatter would remove the extra spaces and line breaks, making it look messy.

### With `RawDescriptionHelpFormatter`:
The examples are displayed exactly as formatted, making them easy to read and copy.

## Result when you run `--help`:

```bash
$ python image_crawler.py --help

usage: image_crawler.py [-h] -q QUERY [-o OUTPUT] [-n MAX] [-d DELAY]

Download images from Bing Image Search

options:
  -h, --help
  ...

Examples:
  python image_crawler.py --query "obama" --output images/obama --max 30
  python image_crawler.py -q "bill gates" -o data/billgates --max 50
  python image_crawler.py -q "elon musk" -o images/elon -n 20
```

The examples stay nicely formatted and indented! 👍

## Other formatter options:
- `HelpFormatter` (default) - Wraps and reformats text
- `RawDescriptionHelpFormatter` - Preserves description formatting
- `RawTextHelpFormatter` - Preserves all help text formatting
- `ArgumentDefaultsHelpFormatter` - Adds default values to help