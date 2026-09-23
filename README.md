# AMD OCR Reader — Mini-Challenge 2 (traffic OCR), LabLab x AMD AI Academy Challenge
Separate solo repo. Packaging-first: the harness grades a Docker container, not a notebook.

## Contract (graded)
`python3 /app/app.py --input-image X` -> `/app/output/X_output.json` `{"text","confidence"}`
Base: `rocm/pytorch:rocm10.0_ubuntu26.04_py3.14_pytorch_release_2.13.0`, 60GB max,
model loaded once (daemon `server.py` + thin client `app.py`), 30s/image, VRAM 1-48GB.

## Local dev (no docker needed)
```powershell
python scripts/make_samples.py
python -m pytest tests/ -q
$env:OCR_BACKEND="stub"; python scripts/selfcheck.py
```
Real model: `$env:OCR_BACKEND="hf"` (Qwen2-VL-2B-Instruct, downloads on first run).
NEVER commit the public registry image reference to this repo.
