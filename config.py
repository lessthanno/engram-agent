"""
Centralized configuration loader.
Priority: env vars > ~/.mind/config.toml > defaults
"""

import os
import re
from pathlib import Path


_CONFIG_PATH = Path("~/.mind/config.toml").expanduser()
_cache = None


def _parse_toml_simple(text: str) -> dict:
    """Minimal TOML parser — handles flat keys and [sections] with string/int/bool/list values."""
    result = {}
    current_section = None
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        # Section header
        m = re.match(r"^\[(.+)\]$", line)
        if m:
            current_section = m.group(1)
            result[current_section] = {}
            continue
        # Key = value
        m = re.match(r'^(\w+)\s*=\s*(.+)$', line)
        if not m:
            continue
        key, val = m.group(1), m.group(2).strip()
        # Parse value
        if val.startswith('"') and val.endswith('"'):
            val = val[1:-1]
        elif val.startswith("'") and val.endswith("'"):
            val = val[1:-1]
        elif val.startswith("["):
            # Simple array of strings
            val = [v.strip().strip('"').strip("'") for v in val[1:-1].split(",") if v.strip()]
        elif val.lower() in ("true", "false"):
            val = val.lower() == "true"
        else:
            try:
                val = int(val)
            except ValueError:
                pass
        target = result[current_section] if current_section else result
        target[key] = val
    return result


def _load_config() -> dict:
    global _cache
    if _cache is not None:
        return _cache

    cfg = {}
    if _CONFIG_PATH.exists():
        try:
            cfg = _parse_toml_simple(_CONFIG_PATH.read_text())
        except Exception as e:
            import logging
            logging.warning(f"config parse failed ({_CONFIG_PATH}): {e}")
    _cache = cfg
    return cfg


def get(section: str, key: str, default=None):
    """Get config value. Env vars override file config."""
    cfg = _load_config()
    env_key = f"MIND_{section.upper()}_{key.upper()}"
    env_val = os.environ.get(env_key)
    if env_val is not None:
        return env_val
    sec = cfg.get(section, {})
    if isinstance(sec, dict):
        return sec.get(key, default)
    return default


# ── Convenience accessors ────────────────────────────────────────────────

def memory_repo() -> Path:
    val = os.environ.get("ENGRAM_MEMORY_REPO") or get("paths", "memory_repo", "~/mind-memory")
    return Path(val).expanduser()


def api_key() -> str:
    return (os.environ.get("ANTHROPIC_API_KEY")
            or os.environ.get("ANTHROPIC_AUTH_TOKEN")
            or get("api", "key", ""))


def api_base_url() -> str:
    return (os.environ.get("ANTHROPIC_BASE_URL")
            or get("api", "base_url", "https://api.anthropic.com"))


def model() -> str:
    return get("api", "model", "claude-sonnet-4-6")


def scan_roots() -> list:
    default = ["~/Documents/01_Projects", "~/code", "~/projects", "~/dev", "~/Desktop"]
    roots = get("git", "scan_roots", default)
    return [Path(r).expanduser() for r in roots]


def git_author_email() -> str:
    return get("git", "author_email", "")


def extra_repos() -> list:
    repos = get("git", "extra_repos", [])
    return [Path(r).expanduser() for r in repos]


def sensitive_patterns() -> list:
    return get("privacy", "sensitive_patterns", [
        r"sk-[a-zA-Z0-9]",
        r"token=\S+",
        r"password[=:]\S+",
        r"secret[=:]\S+",
        r"ANTHROPIC_API_KEY=\S+",
    ])
