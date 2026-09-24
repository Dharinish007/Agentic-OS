# Codex adapter

- **Rules:** synced to `~/.codex/AGENTS.md` (global). Project `AGENTS.md` files are layered on top from the repo root down to the working directory.
- **Skills:** synced to `~/.agents/skills/<name>/` (user scope; symlinks are also supported). Repo skills go in `.agents/skills/`.
- **MCP:** `codex mcp add <name> -- <command>`, or edit `~/.codex/config.toml`:
  ```toml
  [mcp_servers.github]
  command = "npx"
  args = ["-y", "@modelcontextprotocol/server-github"]
  env_vars = ["GITHUB_TOKEN"]   # names only; the value comes from your environment
  ```
  Field names vary between Codex versions. Check `codex mcp --help` before editing.
- **Tool-specific (not synced):** sandbox mode, approval policy, model and profile settings in `config.toml`.
- Docs: https://developers.openai.com/codex/skills
