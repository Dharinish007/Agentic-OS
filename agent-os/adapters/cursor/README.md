# Cursor adapter

- **Global rules: not file-based.** Cursor stores User Rules in Settings → Rules. Paste the contents of `AGENTS.md` there manually and repaste after changes. `sync.ps1` cannot do this.
- **Project rules:** Cursor reads `AGENTS.md` in the project root and `.cursor/rules/*.mdc` (with glob and always-apply frontmatter). Those belong to each project, not here.
- **Skills:** synced to `~/.agents/skills/<name>/`, which Cursor loads globally. Cursor may also load `~/.claude/skills/`, so a skill could appear twice; they are identical copies, so this is harmless.
- **MCP:** `~/.cursor/mcp.json` (global) or `.cursor/mcp.json` (project), key `mcpServers`. Use `${env:VAR}` references; never paste values.
- Docs: https://cursor.com/docs/skills · https://cursor.com/docs
