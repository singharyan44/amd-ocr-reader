"""Dev-only accuracy probe: full pipeline (segment + TrOCR + rules) on CPU.
NOT part of the grading image. Run: python scripts/local_accuracy.py [samples|samples2]
"""
import glob, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app"))
os.environ.setdefault("OCR_BACKEND", "trocr")
os.environ.setdefault("HF_HOME", os.path.expanduser("~/.cache/hf_ocr"))
from preprocess import prepare
from detect import read_image
from backends import get_backend

EXPECTED = {
    "plate_clean.png": "7ABC123", "plate_blur.png": "JHT2951", "plate_dark.png": "5XYZ891",
    "stop_clean.png": "STOP", "stop_noise.png": "STOP",
    "limit_clean.png": "SPEED LIMIT 65", "work_clean.png": "ROAD WORK AHEAD",
    "plaque_35.png": "35",
}


def main():
    d = sys.argv[1] if len(sys.argv) > 1 else "samples2"
    root = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), d)
    be = get_backend()
    print(f"backend={be.name}")
    score = 0
    for p in sorted(glob.glob(os.path.join(root, "*.*"))):
        fn = os.path.basename(p)
        try:
            text, conf = read_image(be, prepare(p))
            exp = EXPECTED.get(fn, "?")
            ok = "OK " if text.replace(" ", "") == exp.replace(" ", "") else "MISS"
            score += ok == "OK "
            print(f"{ok} {fn}: got={text!r} exp={exp!r}")
        except Exception as e:
            print(f"ERR {fn}: {type(e).__name__}: {e}")
    print(f"score computed above (expected map covers samples2)")


if __name__ == "__main__":
    main()
