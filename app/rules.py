"""Transcription rules — mirrors the challenge PDF normalization + conventions.

Normalization (theirs, applied before compare):
  uppercase, remove all whitespace, remove - . _ and interpunct.
Ours (applied before writing, so raw text is already clean):
  - US plates: drop jurisdiction banners/slogans printed AROUND the number
  - Chinese plates: KEEP leading province char + letter (part of registration)
  - Signs: keep all printed words in reading order, lines joined with space
  - Plaques: digits only (no units) — handled by prompt; kept as-is here
  - Never add labels/prefixes/units/explanations.
"""
import re
import unicodedata

# banners/slogans printed around US plate numbers (dropped, never part of answer)
BANNERS = {
    "CALIFORNIA", "TEXAS", "FLORIDA", "NEW YORK", "OHIO", "NEVADA", "ARIZONA",
    "WASHINGTON", "OREGON", "COLORADO", "MICHIGAN", "GEORGIA", "VIRGINIA",
    "NORTH CAROLINA", "SOUTH CAROLINA", "PENNSYLVANIA", "NEW JERSEY",
    "MASSACHUSETTS", "MARYLAND", "ILLINOIS", "OKLAHOMA", "KANSAS",
    "THE LONE STAR STATE", "GOLDEN STATE", "SUNSHINE STATE", "EMPIRE STATE",
    "GRAND CANYON STATE", "EVERGREEN STATE", "GARDEN STATE",
    "DMV", "DEPARTMENT OF MOTOR VEHICLES",
}
# label prefixes models love to add (dropped with their colon)
LABELS = {"PLATE", "LICENSE", "TEXT", "READING", "SIGN", "RESULT", "OUTPUT", "NUMBER"}


def _strip_accents(s):
    return "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c))


def normalize(text):
    """The grader's normalization — use in tests to compare like they do."""
    t = text.upper()
    t = re.sub(r"\s+", "", t)
    for ch in ("-", ".", "_", "·", "•", "∙"):
        t = t.replace(ch, "")
    return t


def clean(raw):
    """Raw VLM output -> submission-ready text."""
    lines = [ln.strip() for ln in raw.strip().splitlines() if ln.strip()]
    # drop label prefixes ("PLATE: 7ABC123" -> "7ABC123")
    fixed = []
    for ln in lines:
        m = re.match(r"^([A-Za-z ]+):\s*(.+)$", ln)
        if m and m.group(1).strip().upper() in LABELS:
            ln = m.group(2)
        fixed.append(ln)
    text = " ".join(fixed)
    text = re.sub(r"\s+", " ", text).strip()
    # drop banner phrases (whole-phrase match, case-insensitive)
    upper = text.upper()
    for b in sorted(BANNERS, key=len, reverse=True):
        upper = re.sub(r"\b" + re.escape(b) + r"\b", " ", upper)
    # if original had CJK, keep original script for those tokens instead
    if re.search(r"[\u4e00-\u9fff]", text):
        # rebuild: keep CJK tokens verbatim, apply banner-drop to latin tokens
        kept = []
        for tok in text.split(" "):
            if re.search(r"[\u4e00-\u9fff]", tok):
                kept.append(tok)
            elif tok.upper() not in BANNERS and tok != "":
                kept.append(tok)
        text = " ".join(kept)
        return re.sub(r"\s+", " ", text).strip()
    text = re.sub(r"\s+", " ", upper).strip()
    return text
