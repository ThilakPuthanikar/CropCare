import json
from pathlib import Path
from datetime import date, datetime, time, timezone

_SEEDS_PATH = Path(__file__).resolve().parent.parent.parent / "database" / "seeds" / "mandi_prices.json"


def _load_mandi_seed_data() -> tuple[list, list]:
    if _SEEDS_PATH.exists():
        try:
            with open(_SEEDS_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                market_series = data.get("weekly_market_series", [])
                snapshot_dates = [date.fromisoformat(d) for d in data.get("weekly_snapshot_dates", [])]
                return market_series, snapshot_dates
        except Exception:
            pass
    return [], []


WEEKLY_MARKET_SERIES, WEEKLY_SNAPSHOT_DATES = _load_mandi_seed_data()


def build_seed_mandi_prices() -> list[dict]:
    records = []
    for market_series in WEEKLY_MARKET_SERIES:
        for snapshot_date, modal_price in zip(WEEKLY_SNAPSHOT_DATES, market_series.get("modal_prices", [])):
            spread = market_series.get("spread", 0)
            records.append(
                {
                    "crop_name": market_series["crop_name"],
                    "district": market_series["district"],
                    "mandi_name": market_series["mandi_name"],
                    "price_per_quintal": float(modal_price),
                    "min_price": float(max(modal_price - spread, 100)),
                    "max_price": float(modal_price + spread),
                    "price_date": snapshot_date,
                    "last_updated": datetime.combine(snapshot_date, time(hour=11, minute=30), tzinfo=timezone.utc),
                }
            )
    return records
