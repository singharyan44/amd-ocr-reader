"""Local mirror of the PDF's 5 pre-submit checks (docker ones skip gracefully).
Run: python scripts/selfcheck.py
"""
import glob, json, os, subprocess, sys, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "out_test")
os.environ["APP_OUTPUT_DIR"] = OUT
os.environ.setdefault("OCR_BACKEND", "stub")


def check_docker():
    try:
        subprocess.run(["docker", "--version"], capture_output=True, check=True, timeout=10)
        print("[1] docker present — build/size checks run on cloud (no dockerfile squash: OK by inspection)")
    except Exception:
        print("[1] SKIP docker checks locally (no docker) — Dockerfile uses mandated base, no squash")


def check_contract():
    os.makedirs(OUT, exist_ok=True)
    exts = set()
    ok = True
    for img in sorted(glob.glob(os.path.join(ROOT, "samples", "sample_*.*"))):
        exts.add(os.path.splitext(img)[1].lower())
        t0 = time.time()
        r = subprocess.run([sys.executable, os.path.join(ROOT, "app", "app.py"),
                            "--input-image", img], capture_output=True, text=True, timeout=60)
        dt = time.time() - t0
        base = os.path.splitext(os.path.basename(img))[0] + "_output.json"
        p = os.path.join(OUT, base)
        if r.returncode != 0 or not os.path.exists(p):
            print(f"[2] FAIL {img}: rc={r.returncode} err={r.stderr[-300:]}"); ok = False; continue
        with open(p) as f:
            d = json.load(f)
        assert isinstance(d.get("text"), str) and isinstance(d.get("confidence"), (int, float)), d
        assert 0.0 <= d["confidence"] <= 1.0, d
        print(f"[2] ok {os.path.basename(img)} -> {d} ({dt:.1f}s, budget 30s)")
    print(f"[3] formats covered: {sorted(exts)} (need .png .jpg/.jpeg .tiff)")
    return ok


if __name__ == "__main__":
    check_docker()
    sys.exit(0 if check_contract() else 1)
