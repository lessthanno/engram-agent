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


def user_name() -> str:
    return get("user", "name", "the user")


def user_context() -> str:
    return get("user", "context", "")


def wiki_title() -> str:
    return get("wiki", "title", "Engram Mind Wiki")


def wiki_motto() -> str:
    return get("wiki", "motto", "")


def scan_roots() -> list:
    default = ["~/code", "~/projects", "~/dev", "~/Desktop", "~/Documents"]
    roots = get("git", "scan_roots", default)
    return [Path(r).expanduser() for r in roots]


def git_author_email() -> str:
    return get("git", "author_email", "")


def extra_repos() -> list:
    repos = get("git", "extra_repos", [])
    return [Path(r).expanduser() for r in repos]


def skills_enabled() -> bool:
    val = get("skills", "enabled", True)
    return val not in ("false", "False", False, 0)


def skill_config(skill_name: str) -> dict:
    """Return config dict for a specific skill from [skills.<name>] section."""
    return _load_config().get(f"skills.{skill_name}", {})


def sensitive_patterns() -> list:
    return get("privacy", "sensitive_patterns", [
        r"sk-[a-zA-Z0-9]",
        r"token=\S+",
        r"password[=:]\S+",
        r"secret[=:]\S+",
        r"ANTHROPIC_API_KEY=\S+",
    ])


# ── Validation ──────────────────────────────────────────────────────────

class ConfigError:
    """A single validation finding."""
    def __init__(self, level: str, key: str, message: str):
        self.level = level  # "error" or "warning"
        self.key = key
        self.message = message

    def __str__(self):
        tag = "ERROR" if self.level == "error" else "WARN"
        return f"[{tag}] {self.key}: {self.message}"


def validate() -> list:
    """Validate config and return list of ConfigError.
    Empty list = all good."""
    issues = []

    # memory_repo must exist
    repo = memory_repo()
    if not repo.exists():
        issues.append(ConfigError("error", "paths.memory_repo",
            f"Directory does not exist: {repo}\n"
            f"  Fix: run 'mkdir -p {repo}' or update ~/.mind/config.toml [paths] memory_repo"))
    elif not (repo / "daily").exists():
        issues.append(ConfigError("warning", "paths.memory_repo",
            f"Missing expected subdirectories in {repo}\n"
            f"  Fix: run 'bash scripts/install.sh' to create the directory structure"))

    # git author email
    email = git_author_email()
    if not email:
        issues.append(ConfigError("warning", "git.author_email",
            "Not set — git collector will capture ALL commits, not just yours\n"
            "  Fix: add author_email under [git] in ~/.mind/config.toml"))

    # scan_roots — at least one should exist
    roots = scan_roots()
    existing_roots = [r for r in roots if r.exists()]
    if not existing_roots:
        issues.append(ConfigError("warning", "git.scan_roots",
            f"None of the scan roots exist: {[str(r) for r in roots]}\n"
            "  Fix: update [git] scan_roots in ~/.mind/config.toml to match your workspace layout"))

    # API access — need at least one method
    import shutil
    has_cli = shutil.which("claude") is not None
    has_key = bool(api_key())
    if not has_cli and not has_key:
        issues.append(ConfigError("warning", "api",
            "No Claude CLI and no API key — synthesis will run in offline mode (limited output)\n"
            "  Fix: install Claude CLI or set [api] key in ~/.mind/config.toml"))

    # model name sanity check
    m = model()
    if m and not any(x in m for x in ["claude", "gpt", "gemini", "llama", "sonnet", "haiku", "opus"]):
        issues.append(ConfigError("warning", "api.model",
            f"Unrecognized model '{m}' — this may fail at synthesis time"))

    # Config file exists at all
    if not _CONFIG_PATH.exists():
        issues.append(ConfigError("warning", "config.toml",
            f"No config file found at {_CONFIG_PATH}\n"
            "  Fix: run 'bash scripts/install.sh' or copy config.toml.example to ~/.mind/config.toml"))

    return issues


def validate_or_warn():
    """Run validation and log any issues. Returns True if no errors."""
    import logging
    logger = logging.getLogger("mind-sync")
    issues = validate()
    errors = 0
    for issue in issues:
        if issue.level == "error":
            logger.error(str(issue))
            errors += 1
        else:
            logger.warning(str(issue))
    return errors == 0
