"""Minimal text preprocessing helpers."""
from __future__ import annotations

from typing import List


def tokenize(text: str) -> List[str]:
    if not text:
        return []
    return [t.strip().lower() for t in text.split() if t.strip()]


def normalize(text: str) -> str:
    if not text:
        return ""
    return " ".join(tokenize(text))
