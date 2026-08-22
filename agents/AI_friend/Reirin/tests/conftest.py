import sys
from pathlib import Path


REIRIN_ROOT = Path(__file__).resolve().parents[1]
AIKO_SRC = REIRIN_ROOT.parent / "Aiko" / "src"
sys.path.insert(0, str(AIKO_SRC))
sys.path.insert(0, str(REIRIN_ROOT / "reconstruction"))

