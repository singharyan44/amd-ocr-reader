"""Synthetic contract samples — verify PNG/JPEG/TIFF handling + JSON shape.
Not training data, not the hidden set. Run: python scripts/make_samples.py
"""
import os
from PIL import Image, ImageDraw

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "samples")


def plate(text, path, fmt):
    img = Image.new("RGB", (400, 200), "white")
    d = ImageDraw.Draw(img)
    d.rectangle([10, 10, 390, 190], outline="blue", width=4)
    d.text((60, 70), text, fill="black")
    img.save(path, fmt)


def sign(lines, path, fmt, bg="red"):
    img = Image.new("RGB", (300, 300), bg)
    d = ImageDraw.Draw(img)
    y = 60
    for ln in lines:
        d.text((40, y), ln, fill="white")
        y += 50
    img.save(path, fmt)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    plate("7ABC123", f"{OUT}/sample_plate.png", "PNG")
    plate("JHT2951", f"{OUT}/sample_plate.jpg", "JPEG")
    sign(["STOP"], f"{OUT}/sample_stop.tiff", "TIFF")
    sign(["SPEED", "LIMIT 65"], f"{OUT}/sample_limit.png", "PNG")
    sign(["ROAD", "WORK", "AHEAD"], f"{OUT}/sample_work.png", "PNG")
    print("wrote", sorted(os.listdir(OUT)))
