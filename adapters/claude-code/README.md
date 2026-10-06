# Claude Code adapter

- **Rules:** synced to `~/.claude/CLAUDE.md` (user-level, all projects). If you already have one, sync reports a conflict. Either move its personal content into the root `AGENTS.md` and rerun with `-Force` (the original is backed up), or keep your file and add the line `@<path-to-agent-os>/AGENTS.md` to it manually.
- **Skills:** synced to `~/.claude/skills/<name>/`. Other skills already in that folder are left untouched. Invoke with `/<name>` or let the agent auto-load them.
- **MCP:** `claude mcp add <name> -- <command>`. Use `--scope user` for all projects or `--scope project` to write `.mcp.json`. Secrets go in `--env` / environment variables, not in `.mcp.json` committed to a repo.
- **Tool-specific (not synced):** `settings.json` permissions (allow/deny), hooks, subagents (`~/.claude/agents/`), output styles, `allowed-tools` / `disable-model-invocation` skill frontmatter.
- **Security:** use hooks and permission deny rules for anything that must never happen. The rules text is guidance, not enforcement.
- Docs: https://code.claude.com/docs/en/memory · https://code.claude.com/docs/en/skills

## Power pack (`plugin/`)
Installed by `sync.ps1` into `~/.claude/skills/agent-os/`, where Claude Code auto-loads it as a plugin (`agent-os@skills-dir`). Check with `claude plugin details agent-os` or `/plugin`.

| Component | What it does |
|---|---|
| `hooks/guard.py` (PreToolUse) | **Denies** catastrophic actions (recursive delete of root/home/cwd, force-push to main/master, mkfs/dd to devices) and secrets written into files. **Asks** before destructive or outward-facing ones (`reset --hard`, `clean -f`, other force-pushes, recursive deletes, `DROP TABLE`, publish/release, `curl | sh`). Needs `python3` or `python` on PATH. Tests: `python adapters/claude-code/plugin/hooks/test_guard.py`. |
| `agents/reviewer.md` | Read-only independent reviewer subagent |
| `agents/researcher.md` | Cited, cross-checked research subagent |
| `commands/` | `/agent-os:idea`, `/agent-os:next`, `/agent-os:verify`, `/agent-os:review` |

The guard is a safety net, not a sandbox: it pattern-matches commands, so unusual phrasings can slip past. Keep permission prompts for anything high-risk.

## Autonomy presets (`presets/`)
```
python adapters/claude-code/apply-preset.py balanced --dry-run
python adapters/claude-code/apply-preset.py balanced     # careful | balanced | full | off
```
Merges only `permissions` into `~/.claude/settings.json` (backup kept). Your own rules are preserved; switching presets removes only rules the previous preset added. All presets deny reading `.env`, `*.pem`, `*.key`.
