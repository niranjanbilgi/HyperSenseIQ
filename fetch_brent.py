import urllib.request, json
from datetime import datetime
import os

os.makedirs("data", exist_ok=True)
price = 90.15

sources = [
    ("Yahoo", "https://query1.finance.yahoo.com/v8/finance/chart/BZ=F?interval=1d&range=1d",
     lambda d: d["chart"]["result"][0]["meta"]["regularMarketPrice"]),
    ("Stooq", "https://stooq.com/q/l/?s=brent.f&f=sd2t2ohlcv&h&e=json",
     lambda d: float(list(d["symbols"].values())[0]["close"])),
    ("AV", "https://www.alphavantage.co/query?function=BRENT&interval=daily&apikey=demo",
     lambda d: float(d["data"][0]["value"])),
]

for name, url, fn in sources:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as r:
            d = json.loads(r.read())
        p = fn(d)
        if 40 < p < 200:
            price = round(p, 2)
            print(f"Brent ${price} from {name}")
            break
    except Exception as e:
        print(f"{name} failed: {e}")

out = {"price_usd": price, "timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"), "source": "Auto"}
with open("data/brent.json", "w") as f:
    json.dump(out, f)
print(f"Saved: {out}")
