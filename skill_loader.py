"""
Skill loader for Engram Agent.
Discovers and loads user-defined skills from ~/.mind/skills/.
Each skill is a directory with SKILL.md (metadata) + skill.py (logic).
"""

import importlib.util
import logging
import re
from pathlib import Path

import config as cfg

log = logging.getLogger("mind-sync")

SKILLS_DIR = Path("~/.mind/skills").expanduser()

_DEFAULT_FUNCTIONS = {
    "collector": "collect",
    "synthesizer": "synthesize",
    "bridge": "bridge",
}


def discover() -> list:
    """Scan ~/.mind/skills/*/SKILL.md and return list of skill metadata dicts."""
    if not SKILLS_DIR.is_dir():
        return []

    # Check global toggle
    global_enabled = cfg.get("skills", "enabled", True)
    if global_enabled in ("false", "False", False, 0):
        return []

    skills = []
    for skill_md in sorted(SKILLS_DIR.glob("*/SKILL.md")):
        try:
            meta = _parse_frontmatter(skill_md.read_text())
            if not meta.get("name") or not meta.get("type"):
                log.warning(f"skill {skill_md.parent.name}: missing name or type, skipping")
                continue
            meta["skill_dir"] = skill_md.parent
            meta.setdefault("entry", "skill.py")
            meta.setdefault("function", _DEFAULT_FUNCTIONS.get(meta["type"], "run"))
            meta.setdefault("enabled", True)

            # Config.toml overrides SKILL.md enabled
            override = cfg.get(f"skills.{meta['name']}", "enabled", None)
            if override is not None:
                meta["enabled"] = override not in ("false", "False", False, 0)

            if meta["enabled"]:
                skills.append(meta)
        except Exception as e:
            log.warning(f"skill {skill_md.parent.name}: load failed: {e}")

    return skills


def load_function(skill_meta: dict):
    """Dynamically import a skill's Python module and return the target function."""
    skill_dir = skill_meta["skill_dir"]
    entry = skill_dir / skill_meta["entry"]
    func_name = skill_meta["function"]

    if not entry.exists():
        raise FileNotFoundError(f"{entry} not found")

    spec = importlib.util.spec_from_file_location(skill_meta["name"], entry)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    fn = getattr(mod, func_name, None)
    if fn is None:
        raise AttributeError(f"{entry} has no function '{func_name}'")
    return fn


def _parse_frontmatter(text: str) -> dict:
    """Extract YAML frontmatter between --- delimiters.
    Minimal parser: handles strings, bools, ints, lists. No PyYAML needed."""
    m = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
    if not m:
        return {}

    result = {}
    for line in m.group(1).splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        # Skip multi-line description continuations (lines starting with whitespace)
        km = re.match(r'^(\w[\w-]*)\s*:\s*(.*)$', line)
        if not km:
            continue
        key, val = km.group(1), km.group(2).strip()

        # Parse value
        if not val or val == '>-':
            # Multi-line string or empty -- skip (description is optional for loading)
            continue
        if val.startswith('"') and val.endswith('"'):
            val = val[1:-1]
        elif val.startswith("'") and val.endswith("'"):
            val = val[1:-1]
        elif val.startswith("["):
            val = [v.strip().strip('"').strip("'") for v in val[1:-1].split(",") if v.strip()]
        elif val.lower() in ("true", "false"):
            val = val.lower() == "true"
        else:
            try:
                val = int(val)
            except ValueError:
                pass

        result[key] = val

    return result
