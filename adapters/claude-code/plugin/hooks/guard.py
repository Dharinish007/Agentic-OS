"""Agent OS guard: PreToolUse hook for Claude Code.

Reads the hook event (JSON) on stdin and answers with a permission decision:
  deny - catastrophic or secret-leaking actions, blocked outright
  ask  - destructive or outward-facing actions, the user must confirm
  (no output) - everything else, normal permission rules apply
Always exits 0; the decision travels in JSON so a missing python3 can fall back to python.
"""
import json
import os
import re
import sys

ROOT_TARGETS = {"/", "/*", "~", "~/", "~/*", "$HOME", "${HOME}", "$HOME/", "*", ".", "./", "..",
                "c:", "c:/", "c:\\", "c:/*", "c:\\*", "$env:userprofile", "%userprofile%"}

DENY_COMMANDS = [
    (r"\bmkfs(\.\w+)?\b", "formats a filesystem"),
    (r"\bdd\b[^|;&]*\bof=/dev/", "writes raw to a device"),
    (r"\bformat(\.com)?\s+[a-z]:", "formats a drive"),
    (r":\(\)\s*\{\s*:\|:&\s*\};:", "fork bomb"),
    (r"\bgit\s+push\b(?=[^|;&]*(\s--force\b|\s-f\b|\s\+))(?=[^|;&]*\b(main|master)\b)",
     "force-pushes to main/master"),
]

ASK_COMMANDS = [
    (r"\bgit\s+push\b[^|;&]*(\s--force(-with-lease)?\b|\s-f\b|\s\+\S)", "force-push rewrites remote history"),
    (r"\bgit\s+push\b[^|;&]*(\s--delete\b|\s:\S)", "deletes a remote branch"),
    (r"\bgit\s+reset\b[^|;&]*--hard", "discards uncommitted work"),
    (r"\bgit\s+clean\b[^|;&]*\s-[a-z]*f", "deletes untracked files"),
    (r"\bgit\s+checkout\b[^|;&]*\s--\s", "discards working-tree changes"),
    (r"\bgit\s+restore\b(?![^|;&]*--staged)", "discards working-tree changes"),
    (r"\bgit\s+branch\b[^|;&]*\s-D\b", "force-deletes a branch"),
    (r"\bgit\s+stash\s+(drop|clear)\b", "deletes stashed work"),
    (r"\bgit\s+(filter-branch|filter-repo)\b", "rewrites history"),
    (r"\bgit\s+rebase\b", "rewrites history"),
    (r"\brm\s+(-\w+\s+)*-\w*[rR]", "recursive delete"),
    (r"\bRemove-Item\b[^|;&]*-Recurse", "recursive delete"),
    (r"\b(rmdir|rd)\s+/s\b", "recursive delete"),
    (r"\bdel\s+[^|;&]*/s\b", "recursive delete"),
    (r"\b(drop\s+(table|database|schema)|truncate\s+table)\b", "destroys database data"),
    (r"\b(npm|pnpm|yarn)\s+publish\b|\btwine\s+upload\b|\bcargo\s+publish\b", "publishes a package"),
    (r"\bgh\s+(release\s+create|pr\s+merge|repo\s+delete)\b", "outward-facing GitHub action"),
    (r"\b(terraform\s+destroy|kubectl\s+delete|docker\s+system\s+prune)\b", "destroys infrastructure"),
    (r"\b(curl|wget|iwr|invoke-webrequest)\b[^;&]*\|\s*(sh|bash|zsh|iex|invoke-expression)\b",
     "runs a downloaded script"),
]

SECRET_PATTERNS = [
    r"AKIA[0-9A-Z]{16}",
    r"\bsk-(ant-)?[A-Za-z0-9_\-]{20,}",
    r"\bgh[pousr]_[A-Za-z0-9]{36}\b",
    r"\bgithub_pat_[A-Za-z0-9_]{40,}",
    r"\bxox[abprs]-[A-Za-z0-9\-]{10,}",
    r"\bAIza[0-9A-Za-z_\-]{35}\b",
    r"-----BEGIN (RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----",
    r"(?i)\b[\w-]*(api[_-]?key|secret|token|passw(or)?d)\b\s*[:=]\s*[\"']([^\"'\s]{16,})[\"']",
]
PLACEHOLDER = re.compile(r"(?i)your|xxx|example|changeme|placeholder|dummy|<|\$\{|\{\{|os\.environ|process\.env")


def decide(decision, reason):
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": decision,
        "permissionDecisionReason": f"Agent OS guard: {reason}",
    }}))
    sys.exit(0)


def recursive_delete_targets(command):
    """Yield the path arguments of rm -r / Remove-Item -Recurse calls."""
    for seg in re.split(r"[|;&]+", command):
        words = seg.split()
        if not words:
            continue
        head = words[0].lower()
        args = words[1:]
        if head == "sudo" and args:
            head, args = args[0].lower(), args[1:]
        flags = [a for a in args if a.startswith("-")]
        if head == "rm" and any(re.match(r"^-\w*[rR]", f) or f == "--recursive" for f in flags):
            yield from (a for a in args if not a.startswith("-"))
        elif head in ("remove-item", "rm", "ri", "del") and any(f.lower().startswith("-r") for f in flags):
            yield from (a for a in args if not a.startswith("-"))


def check_command(command):
    for target in recursive_delete_targets(command):
        if target.strip("\"'").lower().rstrip() in ROOT_TARGETS:
            decide("deny", f"recursive delete of '{target}' (root/home/cwd) is blocked")
    for pattern, why in DENY_COMMANDS:
        if re.search(pattern, command, re.I):
            decide("deny", f"blocked: {why}")
    for pattern, why in ASK_COMMANDS:
        if re.search(pattern, command, re.I):
            decide("ask", f"{why} - confirm this is intended")


def check_write(tool_input):
    path = str(tool_input.get("file_path", ""))
    name = os.path.basename(path).lower()
    if name.startswith(".env") and not name.endswith((".example", ".sample", ".template")):
        return  # .env files are the right place for secrets (keep them git-ignored)
    texts = [tool_input.get("content", ""), tool_input.get("new_string", "")]
    texts += [e.get("new_string", "") for e in tool_input.get("edits", []) if isinstance(e, dict)]
    for text in filter(None, map(str, texts)):
        for pattern in SECRET_PATTERNS:
            for m in re.finditer(pattern, text):
                if not PLACEHOLDER.search(m.group(0)):
                    decide("deny", f"looks like a secret is being written into {name or 'a file'}. "
                                   "Use an environment variable or a git-ignored .env file instead.")


def main():
    try:
        event = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        sys.exit(0)
    tool = event.get("tool_name", "")
    tool_input = event.get("tool_input") or {}
    if tool in ("Bash", "PowerShell"):
        check_command(str(tool_input.get("command", "")))
    elif tool in ("Write", "Edit", "MultiEdit"):
        check_write(tool_input)
    sys.exit(0)


if __name__ == "__main__":
    main()
