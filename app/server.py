"""Container daemon: loads the model ONCE at container start, serves POST /read.
app.py queries this first; per-image execs stay thin (30s budget each).
Stdlib HTTP — no extra deps beyond requirements.
"""
import io, json, os, sys
from http.server import BaseHTTPRequestHandler, HTTPServer

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image
from preprocess import enhance
from detect import read_image
from backends import get_backend

BACKEND = None


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def do_POST(self):
        if self.path != "/read":
            self.send_response(404); self.end_headers(); return
        n = int(self.headers.get("Content-Length", 0))
        img = enhance(Image.open(io.BytesIO(self.body_read(n))).convert("RGB"))
        text, conf = read_image(BACKEND, img)
        body = json.dumps({"text": text, "confidence": float(conf)}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def body_read(self, n):
        return self.rfile.read(n)


if __name__ == "__main__":
    BACKEND = get_backend()  # single load, shared by all 10 test images
    print(f"daemon: backend={BACKEND.name}", flush=True)
    HTTPServer(("127.0.0.1", 8000), Handler).serve_forever()
