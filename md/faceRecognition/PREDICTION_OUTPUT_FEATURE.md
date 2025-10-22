# Face Recognition - Prediction Output Feature

## ✅ Feature Added: Save Predictions to Output Directory

The face recognition system now supports saving prediction results to a specified output directory!

---

## What's New

### Enhanced `infer` Command

The `infer` command now has an optional `--output-dir` parameter that saves:

1. **Annotated Image** - Original image with bounding box and label
2. **JSON Result** - Detailed prediction data in JSON format

---

## Usage

### Basic Inference (No Save)

```bash
python face_recognizer.py infer --img data/obama/obama_001.jpg --bank face_bank.pt
```

**Output:**
```
[info] Using CUDA for InceptionResnetV1 (embedding model)
[info] Using CPU for MTCNN (face detection) to avoid NMS issues
Prediction: obama  (cosine=0.882, det_prob=1.00)
```

### Inference with Save

```bash
python face_recognizer.py infer \
  --img data/obama/obama_001.jpg \
  --bank face_bank.pt \
  --output-dir predictions
```

**Output:**
```
[info] Using CUDA for InceptionResnetV1 (embedding model)
[info] Using CPU for MTCNN (face detection) to avoid NMS issues
Prediction: obama  (cosine=0.882, det_prob=1.00)
[saved] Annotated image saved to predictions\obama_001_predicted.jpg
[saved] Result data saved to predictions\obama_001_result.json
```

---

## Output Files

### 1. Annotated Image (`*_predicted.jpg`)

The annotated image includes:
- ✅ Green bounding box around detected face (recognized person)
- 🔶 Orange bounding box (unknown person)
- 📝 Label with person name and confidence score
- 🎨 Clean background box behind text for better readability

**Visual Example:**
```
┌─────────────────────────────┐
│                             │
│    ┌──────────────┐         │
│    │ obama (0.88) │         │
│    ╔══════════════╗         │
│    ║              ║         │
│    ║    [FACE]    ║         │
│    ║              ║         │
│    ╚══════════════╝         │
│                             │
└─────────────────────────────┘
```

### 2. JSON Result (`*_result.json`)

**Example for recognized person:**
```json
{
  "image": "data/obama/obama_001.jpg",
  "prediction": "obama",
  "cosine_similarity": 0.8824978470802307,
  "detection_probability": 1.0,
  "threshold": 0.55,
  "status": "recognized"
}
```

**Example for no face detected:**
```json
{
  "image": "path/to/image.jpg",
  "prediction": "No face detected",
  "confidence": 0.0,
  "detection_prob": 0.0
}
```

**JSON Fields Explained:**
- `image` - Path to the input image
- `prediction` - Predicted person name or "Unknown"
- `cosine_similarity` - Confidence score (0.0 to 1.0)
- `detection_probability` - Face detection confidence
- `threshold` - Threshold used for recognition
- `status` - "recognized" or "unknown"

---

## Use Cases

### 1. Batch Processing

Process multiple images and save all results:

```bash
# Process Obama images
for img in data/obama/*.jpg; do
  python face_recognizer.py infer --img "$img" --bank face_bank.pt --output-dir predictions/obama
done

# Process Bill Gates images
for img in data/billgates/*.jpg; do
  python face_recognizer.py infer --img "$img" --bank face_bank.pt --output-dir predictions/billgates
done
```

**Windows PowerShell:**
```powershell
# Process all images in a folder
Get-ChildItem data\obama\*.jpg | ForEach-Object {
  python face_recognizer.py infer --img $_.FullName --bank face_bank.pt --output-dir predictions
}
```

### 2. Create Visual Report

Generate annotated images for review:

```bash
python face_recognizer.py infer \
  --img test_images/group_photo.jpg \
  --bank face_bank.pt \
  --output-dir reports/$(date +%Y%m%d)
```

### 3. Data Analysis

Collect prediction data for analysis:

```bash
# Process test dataset
python face_recognizer.py infer --img test1.jpg --bank face_bank.pt --output-dir results
python face_recognizer.py infer --img test2.jpg --bank face_bank.pt --output-dir results

# Analyze results
python -c "
import json
import glob

results = []
for f in glob.glob('results/*_result.json'):
    with open(f) as jf:
        results.append(json.load(jf))

recognized = sum(1 for r in results if r['status'] == 'recognized')
print(f'Recognition rate: {recognized}/{len(results)} = {recognized/len(results)*100:.1f}%')
"
```

### 4. Quality Control

Review predictions with visual annotations:

```bash
# Generate predictions for manual review
python face_recognizer.py infer \
  --img uploaded_photo.jpg \
  --bank face_bank.pt \
  --output-dir review_queue

# Review the annotated image
# (Open review_queue/uploaded_photo_predicted.jpg)
```

---

## Directory Structure

After running predictions with output directory:

```
faceRecognition/
├── predictions/
│   ├── obama_001_predicted.jpg       # Annotated image
│   ├── obama_001_result.json         # Prediction data
│   ├── bill_gates_001_predicted.jpg  # Annotated image
│   └── bill_gates_001_result.json    # Prediction data
├── face_bank.pt
├── face_recognizer.py
└── data/
    ├── obama/
    └── billgates/
```

---

## Advanced Examples

### Custom Threshold with Output

```bash
# More strict recognition (higher threshold)
python face_recognizer.py infer \
  --img test.jpg \
  --bank face_bank.pt \
  --thr 0.70 \
  --output-dir predictions_strict

# More permissive recognition (lower threshold)
python face_recognizer.py infer \
  --img test.jpg \
  --bank face_bank.pt \
  --thr 0.45 \
  --output-dir predictions_permissive
```

### Organize by Date

```bash
# Linux/Mac
OUTPUT_DIR="predictions/$(date +%Y-%m-%d)"
python face_recognizer.py infer \
  --img photo.jpg \
  --bank face_bank.pt \
  --output-dir "$OUTPUT_DIR"

# Windows PowerShell
$OUTPUT_DIR = "predictions\$(Get-Date -Format 'yyyy-MM-dd')"
python face_recognizer.py infer --img photo.jpg --bank face_bank.pt --output-dir $OUTPUT_DIR
```

### Process Unknown Images

```bash
# Test images from unknown sources
python face_recognizer.py infer \
  --img unknown_person.jpg \
  --bank face_bank.pt \
  --output-dir unknown_results

# The system will still save results even if person is "Unknown"
# Result JSON will have: "status": "unknown"
```

---

## Integration Examples

### Python Script

```python
import subprocess
import json
from pathlib import Path

def predict_and_load_result(image_path, output_dir="predictions"):
    """Run prediction and return the result."""
    # Run inference
    subprocess.run([
        "python", "face_recognizer.py", "infer",
        "--img", image_path,
        "--bank", "face_bank.pt",
        "--output-dir", output_dir
    ])
    
    # Load result
    result_file = Path(output_dir) / f"{Path(image_path).stem}_result.json"
    with open(result_file) as f:
        return json.load(f)

# Use it
result = predict_and_load_result("data/obama/obama_001.jpg")
print(f"Person: {result['prediction']}")
print(f"Confidence: {result['cosine_similarity']:.3f}")
```

### Batch Analysis Script

```python
import json
import glob
from pathlib import Path
from collections import Counter

# Load all results
results = []
for json_file in glob.glob("predictions/*_result.json"):
    with open(json_file) as f:
        results.append(json.load(f))

# Statistics
total = len(results)
recognized = sum(1 for r in results if r['status'] == 'recognized')
unknown = sum(1 for r in results if r['status'] == 'unknown')

print(f"Total predictions: {total}")
print(f"Recognized: {recognized} ({recognized/total*100:.1f}%)")
print(f"Unknown: {unknown} ({unknown/total*100:.1f}%)")

# Count predictions by person
predictions = [r['prediction'] for r in results if r['status'] == 'recognized']
counter = Counter(predictions)
print("\nPredictions by person:")
for person, count in counter.most_common():
    print(f"  {person}: {count}")

# Average confidence
avg_confidence = sum(r['cosine_similarity'] for r in results if r['status'] == 'recognized') / recognized
print(f"\nAverage confidence: {avg_confidence:.3f}")
```

---

## File Naming Convention

The output files follow this naming pattern:

- **Input:** `data/obama/obama_001.jpg`
- **Annotated Image:** `predictions/obama_001_predicted.jpg`
- **JSON Result:** `predictions/obama_001_result.json`

The stem of the original filename is preserved, making it easy to track which output corresponds to which input.

---

## Technical Details

### How It Works

1. **Face Detection:** MTCNN detects face location in the image
2. **Face Embedding:** InceptionResnetV1 generates 512-dimensional embedding
3. **Recognition:** Cosine similarity compares embedding to face bank
4. **Annotation:** If output_dir is provided:
   - Draw bounding box around detected face
   - Add label with name and confidence
   - Save annotated image as JPG
5. **JSON Export:** Save all prediction metadata as JSON

### Color Coding

- **Green box (0, 255, 0):** Recognized person (above threshold)
- **Orange box (0, 165, 255):** Unknown person (below threshold)
- **White text on colored background:** For readability

### Performance

- **No overhead when not used:** If `--output-dir` is not specified, no additional processing occurs
- **Minimal overhead when used:** Drawing annotations takes < 0.1 seconds
- **Efficient file I/O:** Uses cv2.imwrite for fast image saving

---

## Testing Results

✅ **Tested successfully:**

```bash
# Obama recognition
python face_recognizer.py infer --img data/obama/obama_001.jpg --bank face_bank.pt --output-dir predictions
# Result: obama (cosine=0.882, det_prob=1.00)
# Files created: obama_001_predicted.jpg, obama_001_result.json

# Bill Gates recognition
python face_recognizer.py infer --img data/billgates/bill_gates_001.jpg --bank face_bank.pt --output-dir predictions
# Result: billgates (cosine=0.907, det_prob=1.00)
# Files created: bill_gates_001_predicted.jpg, bill_gates_001_result.json
```

✅ **Backward compatible:**
- Works with and without `--output-dir`
- All existing functionality preserved

---

## Summary

### New Feature Capabilities

✅ Save annotated images with bounding boxes and labels  
✅ Export prediction data in JSON format  
✅ Optional feature - only activates when `--output-dir` is specified  
✅ Automatic directory creation if it doesn't exist  
✅ Handles both recognized and unknown cases  
✅ Handles no-face-detected cases  
✅ Clean file naming based on input filename  
✅ Ready for batch processing  
✅ Integration-friendly JSON output  

### Command Line Options

```bash
python face_recognizer.py infer \
  --img IMAGE_PATH           # Input image (required)
  --bank BANK_FILE          # Face bank file (default: face_bank.pt)
  --thr THRESHOLD           # Recognition threshold (default: 0.55)
  --output-dir OUTPUT_DIR   # Save results directory (optional)
```

---

## Next Steps

1. **Process your images:** Use `--output-dir` to save predictions
2. **Review results:** Check annotated images and JSON data
3. **Batch process:** Create scripts for multiple images
4. **Analyze data:** Use JSON files for statistics and reporting

Enjoy the new prediction output feature! 🎉

