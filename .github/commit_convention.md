# Commit Message Convention

This project follows [Conventional Commits](https://www.conventionalcommits.org/).
Commit messages are validated by `.commitlintrc.json` in CI.

---

## Format

```
type(scope): short description

Optional longer body explaining the WHY, not the WHAT.
Wrap at 72 characters.

Refs: GHT-123
```

---

## Types

| Type | Description | Example |
|------|-------------|---------|
| `feat` | New feature or capability | `feat(dashboard): add language filter dropdown` |
| `fix` | Bug fix | `fix(pipeline): handle null star count from github api` |
| `chore` | Maintenance, deps, config | `chore(infra): upgrade dlt to 0.5.0` |
| `docs` | Documentation only | `docs: update dbt model dag diagram` |
| `refactor` | Code restructure, no behavior change | `refactor(pipeline): extract retry logic to helper` |
| `test` | Add or update tests | `test(dashboard): add mock for motherduck connection` |
| `ci` | GitHub Actions / CI changes | `ci: add branch name lint to quality gate` |
| `perf` | Performance improvement | `perf(dbt): add index to fct_trending_repos` |

---

## Scopes

| Scope | Covers |
|-------|--------|
| `pipeline` | `pipelines/` — dlt ingestion |
| `dbt` | `dbt/` — models, tests, seeds |
| `dashboard` | `dashboard/` — Streamlit app |
| `infra` | GitHub Actions, Docker, deployment |
| `tests` | `tests/` — pytest suite |
| `docs` | README, AGENTS.md, markdown files |

> Scope is optional but strongly recommended.

---

## Linear Issue Reference

Always include a `Refs:` footer when a commit is linked to a Linear issue:

```
fix(pipeline): handle rate limit retry on github search api

GitHub's search API returns 429 when >10 requests/minute without
an authenticated token. Added exponential backoff with jitter.

Refs: GHT-17
```

For breaking changes, add `BREAKING CHANGE:` in the footer:

```
feat(dbt): rename stars_count to star_count across all models

BREAKING CHANGE: Column renamed in dim_repositories, fct_trending_repos,
and fct_language_trends. Update any downstream queries.

Refs: GHT-88
```

---

## Rules (enforced by CI)

- ✅ Type is required and must be lowercase
- ✅ Scope is optional but must be lowercase if present
- ✅ Subject is required, lowercase, no trailing period, max 72 chars
- ✅ Full header max 100 chars
- ✅ Body/footer must have a blank leading line
- ⚠️ Scope must be from the allowed list (warning, not error)
