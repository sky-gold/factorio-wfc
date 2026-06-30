from __future__ import annotations

import importlib.util
import logging
import sys
from pathlib import Path

MODULE_NAME = "_factorio_wfc"
log = logging.getLogger(__name__)


def load_native_module() -> bool:
    if MODULE_NAME in sys.modules:
        loaded = sys.modules[MODULE_NAME]
        if hasattr(loaded, "validate_snapshot"):
            log.debug("Native module already in sys.modules")
            return True

    root = Path(__file__).resolve().parents[2]
    pyd_dir = root / "build" / "Release"
    log.info("Looking for %s in %s", MODULE_NAME, pyd_dir)

    if not pyd_dir.is_dir():
        log.error("Directory does not exist: %s (run make.bat build)", pyd_dir)
        return False

    candidates = sorted(pyd_dir.glob(f"{MODULE_NAME}*.pyd"))
    if not candidates:
        log.error(
            "No %s*.pyd found in %s — build the C++ extension first (make.bat build)",
            MODULE_NAME,
            pyd_dir,
        )
        return False

    pyd_path = candidates[0]
    log.info("Loading native extension: %s", pyd_path)

    spec = importlib.util.spec_from_file_location(MODULE_NAME, pyd_path)
    if spec is None or spec.loader is None:
        log.error("Failed to create import spec for %s", pyd_path)
        return False

    module = importlib.util.module_from_spec(spec)
    sys.modules[MODULE_NAME] = module
    try:
        spec.loader.exec_module(module)
    except Exception:
        log.exception("exec_module failed for %s", pyd_path)
        sys.modules.pop(MODULE_NAME, None)
        return False

    log.info("Native module loaded (wire v%s)", getattr(module, "wire_format_version", lambda: "?")())
    return True
