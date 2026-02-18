from __future__ import annotations

import os
from typing import Optional

import streamlit as st
import streamlit.components.v1 as components

_RELEASE = True

# When deploying, we serve the prebuilt frontend from this directory
_FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "frontend", "dist")

_component = components.declare_component(
    "voice_guess",
    path=_FRONTEND_DIR if _RELEASE else None,
)

def voice_guess(
    label: str = "🎤 Speak your guess",
    lang: str = "en-US",
    key: str | None = None,
) -> Optional[int]:
    """
    Voice recognition widget.
    Returns an int (0-100) or None if nothing recognized yet.

    Works best in Chrome/Edge. Needs mic permission.
    """
    val = _component(label=label, lang=lang, key=key, default=None)

    # Component may return None or a number
    if val is None:
        return None

    try:
        n = int(val)
    except Exception:
        return None

    # Keep it in range (0–100)
    n = max(0, min(100, n))
    return n
