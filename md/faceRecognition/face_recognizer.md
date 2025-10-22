Gotcha—here’s a clean, working PyTorch setup for face recognition using **facenet-pytorch** (MTCNN for detection + InceptionResnetV1 for embeddings). It supports:

* building an **embedding bank** from a folder of labeled faces,
* **real-time webcam** recognition,
* and a quick **single-image** inference.

### Install

```bash
pip install torch torchvision facenet-pytorch opencv-python pillow
```

### Folder layout (training images)

Put a few clear face images per person:

```
data/
  alice/
    img1.jpg
    img2.jpg
  bob/
    img1.jpg
    img2.jpg
```

---

### `face_recognizer.py`

```python
import argparse
import os
from pathlib import Path
from typing import Dict, List, Tuple

import torch
import torch.nn.functional as F
from PIL import Image
import numpy as np
import cv2

from facenet_pytorch import MTCNN, InceptionResnetV1

# ---------------------------
# Utilities
# ---------------------------
def load_image_paths(root: Path) -> List[Tuple[str, Path]]:
    """
    Returns list of (label, image_path) from a directory structure:
    root/
      person_a/*.jpg
      person_b/*.png
    """
    items = []
    for person_dir in sorted([p for p in root.iterdir() if p.is_dir()]):
        label = person_dir.name
        for img_path in person_dir.glob("*"):
            if img_path.suffix.lower() in {".jpg", ".jpeg", ".png", ".bmp", ".webp"}:
                items.append((label, img_path))
    return items

def cosine_sim(a: torch.Tensor, b: torch.Tensor) -> torch.Tensor:
    """Cosine similarity between two tensors of shape (D,) or (N,D) and (M,D)."""
    a = F.normalize(a, dim=-1)
    b = F.normalize(b, dim=-1)
    return a @ b.T  # (N,M)

def annotate(frame, text, x, y, color=(0, 255, 0)):
    cv2.putText(frame, text, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2, cv2.LINE_AA)

# ---------------------------
# Model setup
# ---------------------------
def create_models(device: str = "cuda" if torch.cuda.is_available() else "cpu"):
    mtcnn = MTCNN(image_size=160, margin=20, post_process=True, device=device)
    resnet = InceptionResnetV1(pretrained='vggface2').eval().to(device)
    return mtcnn, resnet, device

@torch.inference_mode()
def face_embed(pil_img: Image.Image, mtcnn: MTCNN, resnet: InceptionResnetV1, device: str):
    """
    Detects the largest face and returns (embedding(512,), bbox(x1,y1,x2,y2), prob) or (None, None, None).
    """
    # MTCNN returns aligned face tensors when 'return_prob=True' is used with 'mtcnn'
    face_tensor, prob = mtcnn(pil_img, return_prob=True)
    if face_tensor is None:
        return None, None, None
    if isinstance(prob, (list, tuple)):  # if multiple faces returned (batch mode), pick best
        best_idx = int(np.argmax(prob))
        face_tensor = face_tensor[best_idx]
        prob = prob[best_idx]
    emb = resnet(face_tensor.unsqueeze(0).to(device)).squeeze(0).cpu()  # (512,)
    return emb, None, float(prob)

# ---------------------------
# Build embedding bank
# ---------------------------
@torch.inference_mode()
def build_bank(data_dir: str, device: str) -> Tuple[Dict[str, torch.Tensor], Dict[str, torch.Tensor]]:
    """
    Returns:
      - prototypes: mean embedding per label {label: (512,)}
      - examples: stacked embeddings per label {label: (K,512)}
    """
    mtcnn, resnet, device = create_models(device)
    pairs = load_image_paths(Path(data_dir))
    if not pairs:
        raise ValueError(f"No images found in {data_dir}")

    label_to_embs: Dict[str, List[torch.Tensor]] = {}
    for label, img_path in pairs:
        try:
            img = Image.open(img_path).convert("RGB")
        except Exception:
            continue
        emb, _, p = face_embed(img, mtcnn, resnet, device)
        if emb is None or (p is not None and p < 0.9):
            # skip low-confidence detections
            continue
        label_to_embs.setdefault(label, []).append(emb)

    if not label_to_embs:
        raise ValueError("No faces detected to build the bank.")

    prototypes = {}
    examples = {}
    for label, embs in label_to_embs.items():
        stack = torch.stack(embs, dim=0)  # (K,512)
        prototypes[label] = stack.mean(dim=0)
        examples[label] = stack
        print(f"[bank] {label}: {len(embs)} embeddings")

    return prototypes, examples

# ---------------------------
# Predict with prototypes
# ---------------------------
@torch.inference_mode()
def predict_label(emb: torch.Tensor, prototypes: Dict[str, torch.Tensor], thr: float = 0.55) -> Tuple[str, float]:
    """
    Returns (label, score). If best cosine < thr => 'Unknown'.
    """
    labels = list(prototypes.keys())
    proto_stack = torch.stack([prototypes[l] for l in labels], dim=0)  # (C,512)
    sims = cosine_sim(emb.unsqueeze(0), proto_stack).squeeze(0)        # (C,)
    best_idx = int(torch.argmax(sims))
    best_sim = float(sims[best_idx])
    label = labels[best_idx] if best_sim >= thr else "Unknown"
    return label, best_sim

# ---------------------------
# Single-image inference
# ---------------------------
def infer_image(img_path: str, bank_path: str, thr: float):
    data = torch.load(bank_path)
    prototypes = data["prototypes"]
    mtcnn, resnet, device = create_models()
    img = Image.open(img_path).convert("RGB")
    emb, _, p = face_embed(img, mtcnn, resnet, device)
    if emb is None or (p is not None and p < 0.9):
        print("No confident face detected.")
        return
    label, score = predict_label(emb, prototypes, thr)
    print(f"Prediction: {label}  (cosine={score:.3f}, det_prob={p:.2f})")

# ---------------------------
# Webcam loop
# ---------------------------
def webcam(bank_path: str, thr: float, cam_index: int = 0):
    data = torch.load(bank_path)
    prototypes = data["prototypes"]
    mtcnn, resnet, device = create_models()

    cap = cv2.VideoCapture(cam_index)
    if not cap.isOpened():
        raise RuntimeError("Could not open webcam. Try a different --cam-index (e.g., 1).")

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil = Image.fromarray(rgb)

            with torch.inference_mode():
                # Detect faces in batch to draw boxes
                boxes, probs = MTCNN(keep_all=True, device=mtcnn.device)(pil)

            if boxes is not None:
                for box, prob in zip(boxes, probs):
                    x1, y1, x2, y2 = [int(v) for v in box.tolist()]
                    face = pil.crop((x1, y1, x2, y2)).resize((160, 160))
                    emb, _, p = face_embed(face, mtcnn, resnet, device)
                    if emb is None or (p is not None and p < 0.8):
                        label, score = "No face", 0.0
                        color = (0, 0, 255)
                    else:
                        label, score = predict_label(emb, prototypes, thr)
                        color = (0, 255, 0) if label != "Unknown" else (0, 165, 255)
                    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                    annotate(frame, f"{label} ({score:.2f})", x1, max(0, y1 - 10), color)

            cv2.imshow("Face Recognition (q to quit)", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    finally:
        cap.release()
        cv2.destroyAllWindows()

# ---------------------------
# Main CLI
# ---------------------------
def main():
    parser = argparse.ArgumentParser(description="PyTorch Face Recognition (facenet-pytorch)")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_build = sub.add_parser("build", help="Build embedding bank from folder")
    p_build.add_argument("--data-dir", type=str, required=True, help="Root folder with person subfolders")
    p_build.add_argument("--out", type=str, default="face_bank.pt", help="Output .pt path")

    p_infer = sub.add_parser("infer", help="Run single-image inference")
    p_infer.add_argument("--img", type=str, required=True)
    p_infer.add_argument("--bank", type=str, default="face_bank.pt")
    p_infer.add_argument("--thr", type=float, default=0.55)

    p_cam = sub.add_parser("cam", help="Webcam recognition")
    p_cam.add_argument("--bank", type=str, default="face_bank.pt")
    p_cam.add_argument("--thr", type=float, default=0.55)
    p_cam.add_argument("--cam-index", type=int, default=0)

    args = parser.parse_args()

    if args.cmd == "build":
        mtcnn, resnet, device = create_models()
        prototypes, examples = build_bank(args.data_dir, device)
        torch.save({"prototypes": prototypes, "examples": examples}, args.out)
        print(f"[ok] Saved embedding bank → {args.out}")

    elif args.cmd == "infer":
        infer_image(args.img, args.bank, args.thr)

    elif args.cmd == "cam":
        webcam(args.bank, args.thr, args.cam_index)

if __name__ == "__main__":
    main()
```

---

### How to use

1. **Build the bank** (once, after you add training images):

```bash
python face_recognizer.py build --data-dir data --out face_bank.pt
```

2. **Test a single image**:

```bash
python face_recognizer.py infer --img path/to/test.jpg --bank face_bank.pt --thr 0.55
```

3. **Webcam recognition**:

```bash
python face_recognizer.py cam --bank face_bank.pt --thr 0.55 --cam-index 0
```

---

### Tips

* If you get many **Unknown** results, lower `--thr` (e.g., 0.5). If you see false positives, raise it (0.6–0.7).
* Add 5–10 varied images per person (different angles/lighting) for better prototypes.
* GPU is auto-used if available.
* For production accuracy, consider training a classifier (e.g., logistic regression/SVM) **on top of embeddings** instead of using prototype means.

If you want, I can add a quick SVM trainer on the embeddings next.

<br><br><br>

Yes — there are several publicly available face recognition datasets you can use for your project with facenet‑pytorch or other face-recognition models. Here are some good ones, plus things to check before using them:

---

### ✅ Good options

* Labeled Faces in the Wild (LFW) — A classic dataset of ~13,000 labelled face images of various people. ([Kaggle][1])
* VGGFace2 — Large-scale: ~3.3 million images of ~9,131 subjects, with variation in age, pose, illumination. ([arXiv][2])
* UMDFaces — ~ 367,888 annotated faces of 8,277 subjects, with keypoint/pose annotations. ([arXiv][3])
* MegaFace — Very large: “the largest publicly available facial recognition dataset with a million faces and bounding boxes”. ([megaface.cs.washington.edu][4])
* There are many more listed in blogs and aggregator sites (e.g., “19 Free Face Recognition Datasets”). ([Shaip][5])

---

### ⚠️ Things to check / caveats

* **Licensing & usage rights**: Some datasets restrict commercial use or require registration / special request (for example MegaFace).
* **Consent & bias issues**: Many face datasets have ethical/privacy concerns (faces scraped from web, consent unclear), and biases in demographics, lighting, etc.
* **Matching your task**: Some datasets are for *face detection* (finding face boxes), some for *face recognition* (identifying who), some for *face verification* (same or different). Make sure the dataset suits your goal.
* **Size / scale tradeoff**: Larger datasets help deep models, but may require lots of disk space / compute. Smaller datasets are easier to work with for prototyping.
* **Preprocessing**: You’ll need to align faces, crop them, embed them etc. Many datasets provide raw images, not pre-aligned thumbnails.

---

### 🔍 My recommendation for you

Since you built a prototype with facenet-pytorch, you might want something manageable first — e.g.:

* Use LFW or UMDFaces to **experiment** and validate your pipeline.
* Then, if you want a more realistic “in-the-wild” scenario, move to VGGFace2 or MegaFace.
* Also consider creating your own **task-specific dataset** (e.g., 50–100 people in your environment) if you’re deploying a custom recognition system.

---

If you like, I can **fetch download links** (and maybe a small curated subset) of **5–10 public face recognition datasets** (with licensing info) and send you a table. Would you like me to do that?

[1]: https://www.kaggle.com/datasets/atulanandjha/lfwpeople?utm_source=chatgpt.com "LFW - People (Face Recognition) - Kaggle"
[2]: https://arxiv.org/abs/1710.08092?utm_source=chatgpt.com "VGGFace2: A dataset for recognising faces across pose and age"
[3]: https://arxiv.org/abs/1611.01484?utm_source=chatgpt.com "UMDFaces: An Annotated Face Dataset for Training Deep Networks"
[4]: https://megaface.cs.washington.edu/dataset/download.html?utm_source=chatgpt.com "Download - MegaFace - University of Washington"
[5]: https://www.shaip.com/blog/15-free-image-datasets-to-train-facial-recognition-models/?utm_source=chatgpt.com "19 Free Face Recognition Datasets to Boost Your AI Projects in 2025"
