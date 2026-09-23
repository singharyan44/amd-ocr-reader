"""Image preprocessing — PIL only (base image ships torch+PIL).
Handles: EXIF orientation, tiny inputs (upscale), low-light (autocontrast).
Blur/glare/angle robustness comes from the VLM; this just normalizes input.
"""
from PIL import Image, ImageOps

MIN_SIDE = 384  # upscale short side below this for small crops


def load_rgb(path):
    img = Image.open(path)
    img = ImageOps.exif_transpose(img).convert("RGB")
    return img


def enhance(img):
    w, h = img.size
    short = min(w, h)
    if short < MIN_SIDE:
        scale = MIN_SIDE / short
        img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
    # autocontrast (cutoff 1%) lifts low-light/glare without inventing detail
    img = ImageOps.autocontrast(img, cutoff=1)
    return img


def prepare(path):
    return enhance(load_rgb(path))
