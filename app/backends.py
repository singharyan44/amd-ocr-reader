"""Backends: OCR_BACKEND=stub (contract tests, no download) | hf (Qwen2-VL-2B).

Prompt is type-agnostic on purpose — the graded set spans plates, signs,
plaques, clean and adverse. Type-specific handling lives in rules.clean().
"""
import os

PROMPT = (
    "Transcribe exactly the characters printed in this image, in reading order. "
    "Top to bottom for multi-line text. "
    "For a US license plate return ONLY the plate number, without any state name or slogan. "
    "For other plates return every registration character exactly as printed. "
    "For road signs return all printed words and numbers. "
    "Return only the transcription, no labels or explanation."
)


class StubBackend:
    name = "stub"

    def read(self, image):
        return "STOP", 0.0  # fixed string: verifies JSON path, never submitted


class HFBackend:
    name = "hf"
    MODEL_ID = os.environ.get("OCR_MODEL_ID", "Qwen/Qwen2-VL-2B-Instruct")

    def __init__(self):
        import torch
        from transformers import Qwen2VLForConditionalGeneration, AutoProcessor
        self.torch = torch
        device = "cuda" if torch.cuda.is_available() else "cpu"  # cuda==HIP on AMD
        dtype = torch.float16 if device == "cuda" else torch.float32
        self.model = Qwen2VLForConditionalGeneration.from_pretrained(
            self.MODEL_ID, torch_dtype=dtype, trust_remote_code=True,
            cache_dir=os.environ.get("HF_HOME", "/models"))
        self.model.to(device).eval()
        self.processor = AutoProcessor.from_pretrained(
            self.MODEL_ID, trust_remote_code=True,
            cache_dir=os.environ.get("HF_HOME", "/models"))
        self.device = device

    def read(self, image):
        import torch
        messages = [[{"role": "user", "content": [
            {"type": "image", "image": image}, {"type": "text", "text": PROMPT}]}]]
        text = self.processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = self.processor(text=[text], images=[image], return_tensors="pt").to(self.device)
        with torch.no_grad():
            out = self.model.generate(**inputs, max_new_tokens=64)
        gen = [o[len(i):] for i, o in zip(inputs.input_ids, out)]
        text = self.processor.batch_decode(gen, skip_special_tokens=True)[0]
        return text.strip().splitlines()[0] if text.strip() else "", 0.85


_backends = {}


def get_backend():
    kind = os.environ.get("OCR_BACKEND", "stub")
    if kind not in _backends:
        _backends[kind] = HFBackend() if kind == "hf" else StubBackend()
    return _backends[kind]
