from native_loader import load_native_module

load_native_module()

import _factorio_wfc as core

from snapshot import build_minimal_catalog


def ensure_catalog_loaded() -> None:
    core.load_catalog(build_minimal_catalog())


def validate(width: int, height: int, cells: bytes | bytearray) -> tuple[bool, str]:
    result = core.validate_snapshot(width, height, cells)
    return result.is_valid, result.message
