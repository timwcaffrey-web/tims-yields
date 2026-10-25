"""Fetch Treasury par yields and SOFR into data/*.json for the app.

Run by the GitHub Action on a schedule; also runnable locally:
    python3 scripts/update_data.py
"""
import csv
import datetime as dt
import io
import json
import pathlib
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
UA = {"User-Agent": "tims-yields-app (personal dashboard)"}

TREASURY_URL = (
    "https://home.treasury.gov/resource-center/data-chart-center/interest-rates/"
    "daily-treasury-rates.csv/{year}/all?type=daily_treasury_yield_curve"
    "&field_tdr_date_value={year}&page&_format=csv"
)
NYFED_URL = "https://markets.newyorkfed.org/api/rates/secured/{kind}/search.json?startDate={start}&endDate={end}"


def get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
        return r.read().decode("utf-8")


def num(s):
    s = (s or "").strip()
    return float(s) if s and s.upper() != "N/A" else None


def treasury(today):
    """Daily 5/7/10-yr par yields for the past ~12 months."""
    start = today - dt.timedelta(days=380)
    rows = {}
    for year in sorted({start.year, today.year}):
        for r in csv.DictReader(io.StringIO(get(TREASURY_URL.format(year=year)))):
            d = dt.datetime.strptime(r["Date"], "%m/%d/%Y").date()
            if d >= start:
                rows[d.isoformat()] = {
                    "date": d.isoformat(),
                    "ust5": num(r.get("5 Yr")),
                    "ust7": num(r.get("7 Yr")),
                    "ust10": num(r.get("10 Yr")),
                }
    return [rows[k] for k in sorted(rows)]


def sofr(today):
    """Daily SOFR and the 30-day average for the past ~12 months."""
    start = today - dt.timedelta(days=380)
    q = dict(start=start.isoformat(), end=today.isoformat())
    rows = {}
    for r in json.loads(get(NYFED_URL.format(kind="sofr", **q)))["refRates"]:
        rows.setdefault(r["effectiveDate"], {})["sofr"] = r["percentRate"]
    # SOFR averages are keyed by their publication date
    for r in json.loads(get(NYFED_URL.format(kind="sofrai", **q)))["refRates"]:
        rows.setdefault(r["effectiveDate"], {})["avg30"] = r["average30day"]
    return [
        {"date": d, "sofr": rows[d].get("sofr"), "avg30": rows[d].get("avg30")}
        for d in sorted(rows)
    ]


def main():
    today = dt.date.today()
    DATA.mkdir(exist_ok=True)
    out = {
        "treasury": treasury(today),
        "sofr": sofr(today),
        "updated": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    if not out["treasury"] or not out["sofr"]:
        raise SystemExit("A source came back empty; keeping the previous data.")
    (DATA / "rates.json").write_text(json.dumps(out, separators=(",", ":")))
    print(f"treasury {len(out['treasury'])} rows, last {out['treasury'][-1]}")
    print(f"sofr {len(out['sofr'])} rows, last {out['sofr'][-1]}")


if __name__ == "__main__":
    main()
