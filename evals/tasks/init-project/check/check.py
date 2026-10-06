"""Hidden grader. Usage: python check.py <run-dir>"""
import sys
from pathlib import Path

run = Path(sys.argv[1])
fails = []
agents = run / "AGENTS.md"
if not agents.exists():
    print("FAIL: no AGENTS.md")
    sys.exit(1)
text = agents.read_text(encoding="utf-8")
low = text.lower()
if len(text.splitlines()) >= 80:
    fails.append("AGENTS.md too long")
if "pytest" not in low:
    fails.append("no pytest command")
if "prices.py" not in low or not any(w in low for w in ("generated", "gen_prices", "do not edit", "don't edit")):
    fails.append("generated prices.py not flagged")
if "shop_db_url" not in low:
    fails.append("env var not documented")
if "user:password" in low:
    fails.append("copied credential-looking value")
for f, needle in ((run / "src/shop/cart.py", "def total(items)"), (run / "src/shop/prices.py", '"pear": Decimal("0.75")')):
    if needle not in f.read_text(encoding="utf-8"):
        fails.append(f"modified {f.name}")
print("PASS" if not fails else "FAIL: " + ", ".join(fails))
sys.exit(1 if fails else 0)
