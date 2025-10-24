[1 tool called]

This is **`requests.Session()`** - creating a persistent HTTP session object.

## What it does:

**`self.session = requests.Session()`** creates a session object that:
- **Persists settings** across multiple HTTP requests
- **Reuses TCP connections** (connection pooling)
- **Maintains cookies** automatically
- **Stores headers** that apply to all requests

## Why use Session instead of regular requests?

### ❌ Without Session (inefficient):
```python
# Each request creates a new connection
requests.get("https://example.com/image1.jpg")
requests.get("https://example.com/image2.jpg")
requests.get("https://example.com/image3.jpg")
# 3 separate TCP connections = slower
```

### ✅ With Session (efficient):
```python
session = requests.Session()
session.get("https://example.com/image1.jpg")
session.get("https://example.com/image2.jpg")
session.get("https://example.com/image3.jpg")
# Reuses the same connection = faster
```

## Benefits in this crawler:

1. **Performance** 🚀
   - Reuses TCP connections to Bing
   - Faster downloads (no repeated handshakes)

2. **Consistent Headers** 🔧
   ```python
   self.session.headers.update({
       "User-Agent": "Mozilla/5.0..."
   })
   ```
   - Sets User-Agent once
   - Applied to all requests automatically

3. **Cookie Management** 🍪
   - Bing might set cookies
   - Session automatically handles them
   - Looks more like a real browser

4. **Connection Pooling** 🔄
   - Downloads 50 images efficiently
   - Doesn't create 50 separate connections

## Real-world impact:

In this crawler, you're downloading **30-50 images**. Using a Session can make the entire process:
- **20-40% faster** (fewer connection overheads)
- **More reliable** (better connection handling)
- **More realistic** (browser-like behavior)

## Example usage in the code:

```python
# Later in the code:
self.session.get(search_url, timeout=10)  # Uses the session
self.session.get(image_url, timeout=10)   # Reuses connection
```

Great choice for a web crawler! 👍