"""Better synthetic samples: tight crops with LARGE text (TrOCR is line-level;
it reads cropped text regions, not wide scenes) + adverse variants.
Run: python scripts/make_samples2.py
"""
import os, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "samples2")
random.seed(7)


def font(size):
    for name in ("arial.ttf", "C:/Windows/Fonts/arial.ttf", "DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except Exception:
            continue
    return ImageFont.load_default()


def plate_crop(text, path, fmt="PNG", adverse=None):
    img = Image.new("RGB", (480, 160), "white")
    d = ImageDraw.Draw(img)
    d.rectangle([4, 4, 476, 156], outline="blue", width=5)
    f = font(90)
    d.text((40, 30), text, fill="black", font=f)
    img = apply_adverse(img, adverse)
    img.save(path, fmt)


def sign_crop(lines, path, bg="red", adverse=None):
    img = Image.new("RGB", (360, 360), bg)
    d = ImageDraw.Draw(img)
    f = font(72)
    y = 40
    for ln in lines:
        d.text((30, y), ln, fill="white", font=f)
        y += 90
    img = apply_adverse(img, adverse)
    img.save(path)


def apply_adverse(img, kind):
    if kind == "blur":
        return img.filter(ImageFilter.GaussianBlur(2.0))
    if kind == "noise":
        import numpy as np
        a = (255 * (0.5 + 0.5 * __import__("numpy").random.randn(img.size[1], img.size[0], 1))).clip(0, 60)
        n = Image.fromarray((__import__("numpy").zeros((img.size[1], img.size[0], 3)) + a).astype("uint8"), "RGB")
        from PIL import ImageChops
        return ImageChops.add(img, n)
    if kind == "dark":
        from PIL import ImageEnhance
        return ImageEnhance.Brightness(img).enhance(0.45)
    return img


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    plate_crop("7ABC123", f"{OUT}/plate_clean.png")
    plate_crop("JHT2951", f"{OUT}/plate_blur.png", adverse="blur")
    plate_crop("5XYZ891", f"{OUT}/plate_dark.png", adverse="dark")
    sign_crop(["STOP"], f"{OUT}/stop_clean.png")
    sign_crop(["STOP"], f"{OUT}/stop_noise.png", adverse="noise")
    sign_crop(["SPEED", "LIMIT 65"], f"{OUT}/limit_clean.png")
    sign_crop(["ROAD", "WORK", "AHEAD"], f"{OUT}/work_clean.png")
    img = Image.new("RGB", (300, 200), "white")
    d = ImageDraw.Draw(img)
    d.text((90, 60), "35", fill="black", font=font(100))
    img.save(f"{OUT}/plaque_35.png")
    print("wrote", sorted(os.listdir(OUT)))
