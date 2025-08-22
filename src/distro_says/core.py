from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple

DEFAULT_DATA_DIRNAME = "data"           # contains quotes/ and images/
ENV_OVERRIDE = "DISTRO_SAYS_DIR"        # optional env var to override

def resolve_data_dirs(cli_data_dir: Optional[str]) -> Tuple[Path, Path]:
    """
    Resolve (quotes_dir, images_dir) with this precedence:
      1) --data-dir
      2) $DISTRO_SAYS_DIR
      3) ./data relative to the current working directory
    """
    if cli_data_dir:
        base = Path(cli_data_dir).expanduser().resolve()
    elif os.environ.get(ENV_OVERRIDE):
        base = Path(os.environ[ENV_OVERRIDE]).expanduser().resolve()
    else:
        base = (Path.cwd() / DEFAULT_DATA_DIRNAME).resolve()
    return base / "quotes", base / "images"

def load_all_distros(quotes_dir: Path) -> Dict[str, dict]:
    """
    Auto-discover quotes/*.json. Each JSON:
      {
        "name": "Ubuntu",
        "tagline": "Practical defaults that just work.",
        "lines": ["One-liner", "Another"]
      }
    """
    out: Dict[str, dict] = {}
    if not quotes_dir.exists():
        return out
    for p in sorted(quotes_dir.glob("*.json")):
        key = p.stem.lower()
        try:
            payload = json.loads(p.read_text(encoding="utf-8"))
            payload.setdefault("name", key.title())
            payload.setdefault("tagline", "")
            payload.setdefault("lines", [])
            if not isinstance(payload["lines"], list):
                payload["lines"] = []
            out[key] = payload
        except Exception as e:
            print(f"Warning: failed to parse {p}: {e}")
    return out

def detect_distro() -> Optional[str]:
    """
    Try to detect distro via /etc/os-release (Linux).
    Returns lowercase ID (e.g. ubuntu, arch) or None.
    """
    osr = "/etc/os-release"
    if not os.path.exists(osr):
        return None
    try:
        with open(osr, "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("ID="):
                    return line.split("=", 1)[1].strip().strip('"').lower()
    except Exception:
        pass
    return None

ALIASES = {
    "linuxmint": "mint",
    "manjaro": "arch",
    "almalinux": "rhel",
    "rocky": "rhel",
    "opensuse-leap": "opensuse",
    "opensuse-tumbleweed": "opensuse",
    "pop": "ubuntu",
}

def normalize_key(key: str, distros: Dict[str, dict]) -> Optional[str]:
    key = key.lower()
    if key in distros:
        return key
    mapped = ALIASES.get(key)
    if mapped and mapped in distros:
        return mapped
    return None

def load_ascii(images_dir: Path, key: str) -> Optional[str]:
    p = images_dir / f"{key}.txt"
    if p.exists():
        try:
            return p.read_text(encoding="utf-8")
        except Exception as e:
            print(f"Warning: failed to read {p.name}: {e}")
    return None

def pick_message(bundle: dict) -> str:
    lines: List[str] = bundle.get("lines", []) or []
    if not lines:
        return str(bundle.get("tagline", ""))
    import random
    return random.choice(lines)
