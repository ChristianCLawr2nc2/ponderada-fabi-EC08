"""Garante que `cg_solver` e o pacote local do simulador estejam no sys.path."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SIM_DIR = Path(__file__).resolve().parent

for path in (ROOT / "src" / "cg_solver", SIM_DIR):
    text = str(path)
    if text not in sys.path:
        sys.path.insert(0, text)
