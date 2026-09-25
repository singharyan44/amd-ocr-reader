"""Harness entrypoint. Contract (exact):
  python3 /app/app.py --input-image /app/input/image_01.png
  -> writes /app/output/image_01_output.json {"text": str, "confidence": float}

Tries the container daemon first (model loaded once at container start);
falls back to in-process load (local dev / single-image runs).
Local override: APP_OUTPUT_DIR (default /app/output).
"""
import argparse, json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from preprocess import prepare
from rules import clean
from backends import get_backend


def via_daemon(image_path):
    import urllib.request
    with open(image_path, "rb") as f:
        data = f.read()
    req = urllib.request.Request("http://127.0.0.1:8000/read", data=data,
                                 headers={"Content-Type": "application/octet-stream"})
    with urllib.request.urlopen(req, timeout=25) as r:
        return json.loads(r.read().decode())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input-image", required=True)
    a = ap.parse_args()
    src = a.input_image
    base = os.path.splitext(os.path.basename(src))[0]
    outdir = os.environ.get("APP_OUTPUT_DIR", "/app/output")
    os.makedirs(outdir, exist_ok=True)
    try:
        _d = via_daemon(src)
        text, conf = _d["text"], _d.get("confidence", 0.8)
    except Exception:
        img = prepare(src)
        text, conf = get_backend().read(img)
        text = clean(text)
    with open(os.path.join(outdir, base + "_output.json"), "w") as f:
        json.dump({"text": text, "confidence": float(conf)}, f)
    print(json.dumps({"text": text, "confidence": float(conf)}))


if __name__ == "__main__":
    main()
