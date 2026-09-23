#!/bin/bash
# Keeps the container alive for the harness; model loads ONCE in the daemon.
# app.py execs per image stay thin clients (30s budget each).
set -e
export OCR_BACKEND=${OCR_BACKEND:-hf}
export HF_HOME=${HF_HOME:-/models}
export HF_HUB_ENABLE_HF_TRANSFER=${HF_HUB_ENABLE_HF_TRANSFER:-1}
nohup python3 /app/server.py > /var/log/ocr_server.log 2>&1 &
# wait for daemon readiness (max ~9min of the 10min startup budget)
for i in $(seq 1 100); do
  if grep -q "daemon: backend=" /var/log/ocr_server.log 2>/dev/null; then break; fi
  sleep 5
done
tail -f /dev/null
