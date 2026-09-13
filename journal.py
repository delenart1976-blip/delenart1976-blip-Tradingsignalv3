
from pathlib import Path
import csv
FILE=Path("signals.csv")
HEAD=["timestamp","asset","signal","score","entry","sl","tp1","tp2","rr","reason"]
def log(row):
    new=not FILE.exists()
    with FILE.open("a",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=HEAD)
        if new:w.writeheader()
        w.writerow({k:row.get(k,"") for k in HEAD})
