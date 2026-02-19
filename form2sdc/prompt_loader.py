"""Load Form2SDCTemplate.md as system prompt for Gemini.

Searches in order:
1. Package data (installed via pip)
2. Repository root (development)
3. GitHub raw URL (fallback for Colab)
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

# GitHub raw URL for Colab fallback
_GITHUB_RAW_URL = (
    "https://raw.githubusercontent.com/SemanticDataCharter/"
    "Form2SDCTemplate/main/Form2SDCTemplate.md"
)


def load_system_prompt(path: Optional[str | Path] = None) -> str:
    """Load Form2SDCTemplate.md content for use as system prompt.

    Args:
        path: Optional explicit path to Form2SDCTemplate.md.

    Returns:
        Content of Form2SDCTemplate.md.

    Raises:
        FileNotFoundError: If the file cannot be found or fetched.
    """
    # 1. Explicit path
    if path is not None:
        p = Path(path)
        if p.exists():
            return p.read_text(encoding="utf-8")
        raise FileNotFoundError(f"Form2SDCTemplate.md not found at: {path}")

    # 2. Package data (importlib.resources)
    try:
        import importlib.resources as resources

        ref = resources.files("form2sdc") / "Form2SDCTemplate.md"
        if ref.is_file():
            return ref.read_text(encoding="utf-8")
    except (ImportError, AttributeError, TypeError, FileNotFoundError):
        pass

    # 3. Repository root (walk up from this file)
    current = Path(__file__).resolve().parent
    for _ in range(5):
        candidate = current / "Form2SDCTemplate.md"
        if candidate.exists():
            return candidate.read_text(encoding="utf-8")
        current = current.parent

    # 4. GitHub raw URL fallback
    return _fetch_from_github()


def _fetch_from_github() -> str:
    """Fetch Form2SDCTemplate.md from GitHub."""
    try:
        import urllib.request

        with urllib.request.urlopen(_GITHUB_RAW_URL, timeout=30) as response:
            return response.read().decode("utf-8")
    except Exception as e:
        raise FileNotFoundError(
            f"Could not find Form2SDCTemplate.md locally or fetch from GitHub: {e}"
        ) from e
