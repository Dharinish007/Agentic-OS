"""Apply an Agent OS autonomy preset to Claude Code user settings (~/.claude/settings.json).

  python adapters/claude-code/apply-preset.py balanced --dry-run   # show the change
  python adapters/claude-code/apply-preset.py balanced             # apply (backup kept)
  python adapters/claude-code/apply-preset.py off                  # remove what Agent OS added

Only the `permissions` rules this script added before are replaced; your own rules and every other
setting are kept. Added rules are tracked in ~/.claude/agent-os-preset.json.
"""
import argparse
import json
import shutil
from pathlib import Path

PRESETS = Path(__file__).resolve().parent / "presets"
SETTINGS = Path.home() / ".claude" / "settings.json"
STATE = Path.home() / ".claude" / "agent-os-preset.json"
LISTS = ("allow", "ask", "deny")


def main():
    names = sorted(p.stem for p in PRESETS.glob("*.json"))
    ap = argparse.ArgumentParser()
    ap.add_argument("preset", choices=names + ["off"])
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    settings = json.loads(SETTINGS.read_text(encoding="utf-8")) if SETTINGS.exists() else {}
    state = json.loads(STATE.read_text(encoding="utf-8")) if STATE.exists() else {"added": {}, "defaultMode": None}
    perms = settings.setdefault("permissions", {})

    # 1. remove rules a previous preset added
    for key in LISTS:
        prev = set(state["added"].get(key, []))
        if key in perms:
            perms[key] = [r for r in perms[key] if r not in prev]
    if state.get("defaultMode") is not None and perms.get("defaultMode") == state["defaultMode"]:
        perms.pop("defaultMode")

    # 2. add the new preset's rules (skip ones you already had)
    new_state = {"preset": args.preset, "added": {}, "defaultMode": None}
    if args.preset != "off":
        preset = json.loads((PRESETS / f"{args.preset}.json").read_text(encoding="utf-8"))["permissions"]
        for key in LISTS:
            mine = perms.setdefault(key, [])
            added = [r for r in preset.get(key, []) if r not in mine]
            mine.extend(added)
            new_state["added"][key] = added
        if "defaultMode" not in perms:
            perms["defaultMode"] = preset["defaultMode"]
            new_state["defaultMode"] = preset["defaultMode"]
    for key in LISTS:
        if key in perms and not perms[key]:
            perms.pop(key)
    if not perms:
        settings.pop("permissions")

    print(json.dumps({"permissions": settings.get("permissions", {})}, indent=2))
    if args.dry_run:
        print(f"\n(dry run) would write {SETTINGS}")
        return
    if SETTINGS.exists():
        shutil.copy(SETTINGS, SETTINGS.with_suffix(".json.agent-os-backup"))
    SETTINGS.parent.mkdir(parents=True, exist_ok=True)
    SETTINGS.write_text(json.dumps(settings, indent=2) + "\n", encoding="utf-8")
    STATE.write_text(json.dumps(new_state, indent=2) + "\n", encoding="utf-8")
    print(f"\nApplied '{args.preset}' to {SETTINGS} (backup: settings.json.agent-os-backup). Restart Claude Code.")


if __name__ == "__main__":
    main()
