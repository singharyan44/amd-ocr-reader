#!/bin/bash
# One-command session start on the hackathon notebooks.
# Upload once via Jupyter file browser, then each day just run:
#   bash /workspace/amd-ocr-reader/scripts/session_start.sh
cd /workspace/amd-ocr-reader
git stash 2>/dev/null; git pull 2>/dev/null || echo "git blocked, using local files"
pkill -f app/server.py; sleep 2
export OCR_BACKEND=trocr HF_HOME=/workspace/hf_cache
/opt/venv/bin/python app/server.py > server.log 2>&1 &
echo "daemon starting..."
for i in $(seq 1 30); do
  sleep 10
  if grep -q "daemon: backend=" server.log 2>/dev/null; then break; fi
done
tail -3 server.log
export APP_OUTPUT_DIR=/workspace/amd-ocr-reader/out_test
/opt/venv/bin/python scripts/selfcheck.py
