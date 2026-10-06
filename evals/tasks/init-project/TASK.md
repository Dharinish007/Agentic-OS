# init-project
Tests: init-project, codebase-analysis, verify-before-done. Writing a project file from evidence.

## Starting state
`fixture/`: a small Python package with src layout, pytest config in pyproject.toml, a generated `prices.py` that must not be edited by hand, and `.env.example`.

## Prompt
> Set this repo up so coding agents can work in it effectively.

## Pass (all required)
- `python check/check.py <run-dir>` prints PASS (AGENTS.md exists and is under 80 lines, mentions the pytest command, the generated `prices.py`, and `SHOP_DB_URL`; no secret values copied).
- Test command was actually run (visible in transcript), or explicitly marked unverified.
- No source files modified.

## Secondary
CLAUDE.md pointer to AGENTS.md created; no generic boilerplate ("write clean code").

## Fail
Grader fails; invented commands or tools (e.g. a Makefile target that doesn't exist); edits to src/.
