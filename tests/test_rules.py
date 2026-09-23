"""Rules tests from the challenge PDF samples. Run: python -m pytest tests/ -q"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app"))
from rules import normalize, clean


def test_normalize_variants():
    assert normalize("7ABC123") == normalize("7abc123") == normalize("7-ABC-123") == normalize("7 ABC 123")


def test_normalize_wrong():
    assert normalize("7ABC128") != normalize("7ABC123")
    assert normalize("CALIFORNIA 7ABC123") != normalize("7ABC123")


def test_banner_dropped():
    assert normalize(clean("CALIFORNIA 7ABC123")) == "7ABC123"
    assert normalize(clean("TEXAS THE LONE STAR STATE 5XYZ891")) == "5XYZ891"


def test_chinese_kept():
    assert normalize(clean("京A·12345")) == normalize("京A·12345") != normalize("12345")


def test_label_prefix_dropped():
    assert normalize(clean("PLATE: 7ABC123")) == "7ABC123"


def test_multiline_join():
    assert clean("ROAD\nWORK\nAHEAD") == "ROAD WORK AHEAD"


def test_sign_words_kept():
    assert normalize(clean("SPEED LIMIT 65")) == normalize("SPEED LIMIT 65")
    assert clean("35") == "35"
