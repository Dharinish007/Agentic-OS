# Antigravity adapter

Paths from the official docs (checked 2026-10-07): [Rules](https://antigravity.google/docs/rules/) · [Skills](https://antigravity.google/docs/skills/) · [Hooks](https://antigravity.google/docs/hooks). Applies to Antigravity 2.0 and Antigravity IDE.

| Item | Synced to | Notes |
|---|---|---|
| Rules | `~/.gemini/GEMINI.md` | Plain Markdown, always on. **Shared with Gemini CLI** (same file), so syncing both tools never duplicates rules. Rules are cumulative: everything in `~/.gemini/AGENTS.md`, `~/.gemini/config/{AGENTS,GEMINI}.md` and `~/.gemini/config/rules/*.md` is also loaded. |
| Skills | `~/.gemini/config/skills/<name>/` | Same `SKILL.md` format. Workspace skills: `<repo>/.agents/skills/`. |
| Guard hook | `~/.gemini/config/agent-os/guard.py` + `~/.gemini/config/hooks.json` | Same guard as Claude Code. Antigravity events (`toolCall.name` = `run_command`, `write_to_file`, `replace_file_content`, `multi_replace_file_content`) are answered with `{"decision": "deny" \| "ask", "reason": ...}`; no opinion = `{}`. `hooks.json` is generated with this machine's absolute path; requires `python` on PATH. |
| MCP | not synced | `~/.gemini/config/mcp_config.json` (global) or `<repo>/.agents/mcp_config.json`. |
| Permissions / autonomy | not synced | Set terminal and review policies in Antigravity settings. Map the presets from `docs/POWER.md` manually. |
| Antigravity CLI | not synced | Uses `~/.gemini/antigravity-cli/{rules,skills}`. Add when needed. |

## Budget warning
Antigravity limits always-on rules to ~20,000 tokens in total (24 KB per file) and demotes the largest files to on-demand pointers when over budget. Large third-party rule packs in `~/.gemini/config/rules/` compete with Agent OS rules for that budget. Keep always-on rules small; move procedures into skills.

## Unverified
- Hook behavior on empty or `{}` output is not documented; the guard returns `{}` to mean "no decision".
- Which shell runs hook commands is not documented; the command works in PowerShell, cmd and bash.
- Exact argument names of `multi_replace_file_content` are not documented; the guard scans every `*Content` field except `TargetContent`.
