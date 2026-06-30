import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "gui" / "src"))

from native_loader import load_native_module

load_native_module()
