"""Offline release checks for the public OddsLab research beta."""
import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
html = (ROOT / "docs/index.html").read_text(encoding="utf-8")
data = json.loads((ROOT / "docs/data.json").read_text(encoding="utf-8"))
manifest = json.loads((ROOT / "docs/manifest.json").read_text(encoding="utf-8"))

assert "<html" in html.lower() and "</html>" in html.lower()
assert "EXPERIMENTELLT" in html
assert "Inga validerade EV-kandidater" in html
assert "MAX_QUOTE_AGE_MS=3*60*60*1000" in html
assert "bookmaker_updated||r.collected_at" in html
assert "INAKTUELLT" in html
assert 'cache:"no-store"' in html
assert "setInterval(" in html
assert manifest["display"] == "standalone"
assert manifest["start_url"].startswith("./")
assert isinstance(data.get("observations"), list)
datetime.fromisoformat(data["updated_at"].replace("Z", "+00:00"))
for i, row in enumerate(data["observations"]):
    for field in ("event_id", "competition", "home", "away", "start", "bookmaker",
                  "selection", "odds", "collected_at"):
        assert row.get(field) is not None, (i, field)
    assert 1 < float(row["odds"]) < 1000, i
    for field in ("start", "collected_at"):
        parsed = datetime.fromisoformat(row[field].replace("Z", "+00:00"))
        assert parsed.tzinfo is not None, (i, field)
    if row.get("bookmaker_updated"):
        parsed = datetime.fromisoformat(row["bookmaker_updated"].replace("Z", "+00:00"))
        assert parsed.tzinfo is not None, (i, "bookmaker_updated")
assert not re.search(r"\bgaranterad (vinst|avkastning)\b", html, re.I)
print(f"Beta static checks passed: {len(data['observations'])} timestamped observations.")
