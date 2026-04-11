# Open Tasks — 2026-04-10

Extracted from activity across all sources. Sorted by staleness.

## Active (touched today)

- [ ] **Auth middleware rewrite** — `xerpa-api/auth/`
  - Status: 2 PRs merged, token revocation still open
  - Last commit: 18:42 today
  - Next step: implement revocation list (research done, code not started)

- [ ] **Login flow UI** — `xerpa-web/src/pages/login/`
  - Status: basic flow working, error states incomplete
  - Last commit: 16:15 today

## Stale (no activity in 2+ days)

- [ ] **Rate limiter TODO** — `xerpa-api/middleware/rate_limit.go:47`
  - Written: Apr 8
  - No commits to this file since
  - Risk: forgotten

- [ ] **PR #142 review** — requested by @chen on Apr 9
  - 0 comments from you
  - Getting stale

- [ ] **Dashboard metrics query optimization** — `xerpa-web/src/api/metrics.ts`
  - Last touched: Apr 6
  - You noted "N+1 query, fix later" in a Claude session
  - No follow-up since

## Completed This Week

- [x] JWT refresh token rotation (Apr 10)
- [x] Session middleware chain rewrite (Apr 10)
- [x] CI pipeline fix for Go 1.22 (Apr 8)
- [x] README update for engram-agent (Apr 7)
