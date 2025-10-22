import argparse
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
    cv2.putText(
        frame, text, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2, cv2.LINE_AA
    )


# ---------------------------
# Model setup
# ---------------------------
def create_models(device: str = "cuda" if torch.cuda.is_available() else "cpu"):
    # MTCNN on CPU to avoid torchvision CUDA NMS issues
    # ResNet on GPU/CPU as requested (ResNet is the heavy model)
    mtcnn_device = "cpu"
    resnet_device = device

    # Check if CUDA is available but force MTCNN to CPU
    if device == "cuda":
        print("[info] Using CUDA for InceptionResnetV1 (embedding model)")
        print("[info] Using CPU for MTCNN (face detection) " "to avoid NMS issues")
    else:
        print("[info] Using CPU for both models")

    mtcnn = MTCNN(image_size=160, margin=20, post_process=True, device=mtcnn_device)
    resnet = InceptionResnetV1(pretrained="vggface2").eval().to(resnet_device)
    return mtcnn, resnet, resnet_device


@torch.inference_mode()
def face_embed(
    pil_img: Image.Image, mtcnn: MTCNN, resnet: InceptionResnetV1, device: str
):
    """
    Detects the largest face and returns (embedding(512,), bbox(x1,y1,x2,y2), prob) or (None, None, None).
    """
    # MTCNN returns aligned face tensors when 'return_prob=True' is used with 'mtcnn'
    face_tensor, prob = mtcnn(pil_img, return_prob=True)
    if face_tensor is None:
        return None, None, None
    if isinstance(
        prob, (list, tuple)
    ):  # if multiple faces returned (batch mode), pick best
        best_idx = int(np.argmax(prob))
        face_tensor = face_tensor[best_idx]
        prob = prob[best_idx]
    emb = resnet(face_tensor.unsqueeze(0).to(device)).squeeze(0).cpu()  # (512,)
    return emb, None, float(prob)


# ---------------------------
# Build embedding bank
# ---------------------------
@torch.inference_mode()
def build_bank(
    data_dir: str, device: str
) -> Tuple[Dict[str, torch.Tensor], Dict[str, torch.Tensor]]:
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
        except Exception as e:
            print(f"[skip] Could not load {img_path}: {e}")
            continue

        try:
            emb, _, p = face_embed(img, mtcnn, resnet, device)
        except Exception as e:
            print(f"[skip] Face detection failed for {img_path.name}: {e}")
            continue

        if emb is None or (p is not None and p < 0.9):
            # skip low-confidence detections
            print(f"[skip] Low confidence or no face in {img_path.name}")
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
def predict_label(
    emb: torch.Tensor, prototypes: Dict[str, torch.Tensor], thr: float = 0.55
) -> Tuple[str, float]:
    """
    Returns (label, score). If best cosine < thr => 'Unknown'.
    """
    labels = list(prototypes.keys())
    proto_stack = torch.stack([prototypes[label] for label in labels], dim=0)  # (C,512)
    sims = cosine_sim(emb.unsqueeze(0), proto_stack).squeeze(0)  # (C,)
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
        raise RuntimeError(
            "Could not open webcam. Try a different --cam-index (e.g., 1)."
        )

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil = Image.fromarray(rgb)

            with torch.inference_mode():
                # Detect faces in batch to draw boxes
                boxes, probs = mtcnn.detect(pil)

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
                    annotate(
                        frame, f"{label} ({score:.2f})", x1, max(0, y1 - 10), color
                    )

            cv2.imshow("Face Recognition (q to quit)", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    finally:
        cap.release()
        cv2.destroyAllWindows()


# ---------------------------
# Main CLI
# ---------------------------
def main():
    parser = argparse.ArgumentParser(
        description="PyTorch Face Recognition (facenet-pytorch)"
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_build = sub.add_parser("build", help="Build embedding bank from folder")
    p_build.add_argument(
        "--data-dir", type=str, required=True, help="Root folder with person subfolders"
    )
    p_build.add_argument(
        "--out", type=str, default="face_bank.pt", help="Output .pt path"
    )

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
