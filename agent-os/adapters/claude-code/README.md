# Claude Code adapter

- **Rules:** synced to `~/.claude/CLAUDE.md` (user-level, all projects). If you already have one, sync reports a conflict. Either move its personal content into the root `AGENTS.md` and rerun with `-Force` (the original is backed up), or keep your file and add the line `@<path-to-agent-os>/AGENTS.md` to it manually.
- **Skills:** synced to `~/.claude/skills/<name>/`. Other skills already in that folder are left untouched. Invoke with `/<name>` or let the agent auto-load them.
- **MCP:** `claude mcp add <name> -- <command>`. Use `--scope user` for all projects or `--scope project` to write `.mcp.json`. Secrets go in `--env` / environment variables, not in `.mcp.json` committed to a repo.
- **Tool-specific (not synced):** `settings.json` permissions (allow/deny), hooks, subagents (`~/.claude/agents/`), output styles, `allowed-tools` / `disable-model-invocation` skill frontmatter.
- **Security:** use hooks and permission deny rules for anything that must never happen. The rules text is guidance, not enforcement.
- Docs: https://code.claude.com/docs/en/memory · https://code.claude.com/docs/en/skills
