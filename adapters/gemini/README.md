# Gemini CLI / Antigravity adapter

- **Rules:** synced to `~/.gemini/GEMINI.md` (global). Optional alternative: set `"context": { "fileName": ["AGENTS.md", "GEMINI.md"] }` in `~/.gemini/settings.json` so project `AGENTS.md` files are read too.
- **Skills:** synced to `~/.agents/skills/<name>/` (Gemini CLI also reads `~/.gemini/skills/`). A skill must be at `<dir>/<name>/SKILL.md`, one level deep.
- **MCP:** `~/.gemini/settings.json` → `"mcpServers": { "<name>": { "command": ..., "args": [...], "env": { "TOKEN": "$TOKEN" } } }`. Reference environment variables; never paste values.
- **Antigravity:** separate app with its own rules/workflows UI and MCP config. It is reported to read `~/.gemini/GEMINI.md`, but this is **unverified**; check in the app before relying on it.
- **Tool-specific (not synced):** sandbox, tool allow/exclude lists, and trust settings in `settings.json`.
- Docs: https://geminicli.com/docs/cli/skills/ · https://google-gemini.github.io/gemini-cli/docs/cli/gemini-md.html
