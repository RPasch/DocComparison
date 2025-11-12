from pathlib import Path
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Output folder (created if missing)
OUTPUT_DIR = Path(__file__).resolve().parents[2] / "outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def resolve_output(*parts: str) -> Path:
    """
    Convenience to put files under outputs/.
    """
    p = OUTPUT_DIR.joinpath(*parts)
    p.parent.mkdir(parents=True, exist_ok=True)
    return p

def get_env(name: str, default: str | None = None) -> str | None:
    return os.getenv(name, default)
