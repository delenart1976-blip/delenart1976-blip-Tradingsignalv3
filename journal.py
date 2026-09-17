"""Persistent paper-trading journal."""

from pathlib import Path
import csv

FILE = Path("signals.csv")
HEAD = ["timestamp", "asset", "signal", "score", "entry", "sl", "tp1", "tp2", "rr", "reason"]


def log(row: dict) -> None:
    new = not FILE.exists() or FILE.stat().st_size == 0
    with FILE.open("a", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=HEAD)
        if new:
            writer.writeheader()
        writer.writerow({key: row.get(key, "") for key in HEAD})


def history(limit: int = 100):
    if not FILE.exists():
        return []
    with FILE.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))[-limit:][::-1]
