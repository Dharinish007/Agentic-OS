# Adapters

Only tool-specific knowledge lives here. Rules and skills are never copied into this folder; `sync.ps1` projects them from the root.
Flow is one-way: **edit the source here → run `sync.ps1`**. Edits at a destination are reported as conflicts, never pulled back.

## Where each tool reads things (from official docs, 2026-09; Antigravity 2026-10)

| | Claude Code | Antigravity | Codex | Gemini CLI | Cursor |
|---|---|---|---|---|---|
| Global rules | `~/.claude/CLAUDE.md` | `~/.gemini/GEMINI.md` (+ `~/.gemini/config/rules/*.md`) | `~/.codex/AGENTS.md` | `~/.gemini/GEMINI.md` | User Rules in Settings UI (no file) |
| Project rules | `CLAUDE.md` (can also read `AGENTS.md`) | `AGENTS.md`, `GEMINI.md`, `.agents/rules/*.md` | `AGENTS.md` | `GEMINI.md` (`context.fileName` can add `AGENTS.md`) | `AGENTS.md`, `.cursor/rules/*.mdc` |
| Global skills | `~/.claude/skills/` | `~/.gemini/config/skills/` | `~/.agents/skills/` | `~/.gemini/skills/` or `~/.agents/skills/` | `~/.agents/skills/`, `~/.cursor/skills/` |
| MCP config | `claude mcp add` → `~/.claude.json`, `.mcp.json` | `~/.gemini/config/mcp_config.json` | `~/.codex/config.toml` (TOML) | `~/.gemini/settings.json` | `~/.cursor/mcp.json` |

`sync.ps1` targets: rules → the global rules file per tool (Antigravity and Gemini CLI share `~/.gemini/GEMINI.md`); skills → `~/.claude/skills` (Claude), `~/.gemini/config/skills` (Antigravity), `~/.agents/skills` (Codex, Gemini, Cursor). Power packs: Claude Code plugin, Antigravity guard hook.

## Portability

| Item | Class | Handling |
|---|---|---|
| Rule content (`AGENTS.md`) | Portable | Copied under each tool's filename |
| Skill content (`SKILL.md`, name + description) | Portable | Copied; Agent Skills standard |
| Skill discovery path | Partially portable | Two targets cover all four tools |
| Tool-only frontmatter (`allowed-tools`, invocation control) | Tool-specific | Not used in source skills |
| MCP catalog (`mcp/registry.md`) | Portable | Read in place; not synced |
| MCP config / transport / env passing | Tool-specific | Manual per tool, see each README |
| OAuth, API keys | Tool-specific | Never handled by this system |
| Permissions, sandbox, hooks | Tool-specific | Configured in each tool |
| Cursor global user rules | Unsupported by files | Paste manually |
| Hidden system prompt, context/compaction strategy | Not portable | Out of scope |
