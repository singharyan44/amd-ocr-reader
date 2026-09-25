"""Line segmentation: TrOCR reads single text lines; graded images hold plates
in scenes and multi-line signs. Split into line strips first, OCR each.
OpenCV only (no downloads). Tuned for printed plates/signs, not handwriting.
"""
import cv2
import numpy as np
from PIL import Image


def segment_lines(pil_img, min_h=12):
    gray = np.array(pil_img.convert("L"))
    # adaptive threshold survives glare / low light / uneven illumination
    bw = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                               cv2.THRESH_BINARY_INV, 51, 9)
    # join characters into line blobs with a wide horizontal kernel
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 7))
    dilated = cv2.dilate(bw, kernel, iterations=2)
    contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    W, H = pil_img.size
    boxes = []
    for c in contours:
        x, y, w, h = cv2.boundingRect(c)
        if h < min_h or w < 30 or w * h < 0.002 * W * H:
            continue
        boxes.append((x, y, w, h))
    boxes.sort(key=lambda b: (b[1], b[0]))
    # merge vertically overlapping boxes (one line split by gaps)
    merged = []
    for b in boxes:
        if merged and b[1] < merged[-1][1] + merged[-1][3]:
            x0 = min(merged[-1][0], b[0]); y0 = min(merged[-1][1], b[1])
            x1 = max(merged[-1][0] + merged[-1][2], b[0] + b[2])
            y1 = max(merged[-1][1] + merged[-1][3], b[1] + b[3])
            merged[-1] = (x0, y0, x1 - x0, y1 - y0)
        else:
            merged.append(b)
    strips = []
    for (x, y, w, h) in merged:
        pad = 6
        x0, y0 = max(0, x - pad), max(0, y - pad)
        x1, y1 = min(W, x + w + pad), min(H, y + h + pad)
        strips.append(pil_img.crop((x0, y0, x1, y1)))
    return strips


def read_image(backend, image):
    """Full pipeline: segment -> read each strip -> join top-to-bottom."""
    from rules import clean
    strips = segment_lines(image) or [image]
    texts, confs = [], []
    for s in strips:
        t, c = backend.read(s)
        t = clean(t)
        if t:
            texts.append(t)
            confs.append(c)
    if not texts:
        return "", 0.0
    return " ".join(texts), sum(confs) / len(confs)
