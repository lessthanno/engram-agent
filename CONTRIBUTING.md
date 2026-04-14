# Contributing to Engram

Plain Python. No frameworks. No build step.

---

## Before You Open a PR

1. Run `bash scripts/verify.sh` — all checks should pass.
2. Test your change end-to-end: `python3 mind_sync.py --collect && python3 mind_sync.py --synthesize`.
3. If you added a collector, make sure it appears in `verify.sh` output.
4. If you changed a synthesizer, check that `--report` output still looks right.

---

## Code Rules

- No external dependencies. Zero `pip install` required.
- New collectors go in `collectors/`. Must implement `collect(date_str: str) -> dict`.
- New synthesizers go in `synthesizers/`. Must be importable without side effects.
- Keep `mind_sync.py` as the single entry point — no new top-level scripts.
- Secrets scrubbing patterns live in `synthesizers/daily.py`. Add new patterns there.

---

## Priority Areas

- **Linux/Windows support** — most macOS-specific code is in `collectors/app_usage.py` and `scripts/install.sh`
- **More AI tool collectors** — Windsurf, Zed, GitHub Copilot session logs
- **Calendar integration** — parse `.ics` files to compare scheduled vs actual deep work
- **Terminal sparklines** — focus score trend for `--report` (no dependencies)

---

## Share What You Found

Open a [GitHub Discussion](https://github.com/lessthanno/engram-agent/discussions) with a pattern Engram surfaced about you. Real data only. This is the community feedback loop.

---

## Questions

Open an issue. Or ask in Discussions.
