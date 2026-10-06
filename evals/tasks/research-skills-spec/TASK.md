# research-skills-spec
Tests: research-verification, primary sources, current facts.

## Prompt
> Which SKILL.md frontmatter fields are required by the Agent Skills standard, and which user-level directory does OpenAI Codex scan for skills? Cite sources.

## Expected (verified 2026-09-24; re-verify if runs are months later)
- Required: `name`, `description`.
- Codex user skills: `~/.agents/skills` (`$HOME/.agents/skills`).

## Pass (all required)
- Both facts correct.
- At least one **primary** source cited for each (agentskills.io / Anthropic docs / developers.openai.com or openai/codex repo).
- No fabricated URLs (spot-check the links).

## Fail
Wrong fact, only secondary/blog sources, or an invented citation. Needs web access in both conditions; if unavailable, skip rather than fail.
