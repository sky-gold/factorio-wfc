from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

MODULE_NAME = "_factorio_wfc"


def load_native_module() -> None:
    if MODULE_NAME in sys.modules:
        loaded = sys.modules[MODULE_NAME]
        if hasattr(loaded, "validate_snapshot"):
            return

    root = Path(__file__).resolve().parents[1]
    pyd_dir = root / "build" / "Release"
    candidates = sorted(pyd_dir.glob(f"{MODULE_NAME}*.pyd"))
    if not candidates:
        return

    spec = importlib.util.spec_from_file_location(MODULE_NAME, candidates[0])
    if spec is None or spec.loader is None:
        return

    module = importlib.util.module_from_spec(spec)
    sys.modules[MODULE_NAME] = module
    spec.loader.exec_module(module)
