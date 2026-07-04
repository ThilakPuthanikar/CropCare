from datetime import date, datetime, time, timezone


WEEKLY_MARKET_SERIES = [
    {
        "crop_name": "Tomato",
        "district": "Bagalkot",
        "mandi_name": "Bagalkot APMC",
        "modal_prices": [1300, 1450, 1200, 1550, 1800, 2250, 2050, 1880],
        "spread": 260,
    },
    {
        "crop_name": "Onion",
        "district": "Bagalkot",
        "mandi_name": "Bagalkot APMC",
        "modal_prices": [1850, 1780, 1920, 2080, 2240, 2410, 2350, 2190],
        "spread": 220,
    },
    {
        "crop_name": "Groundnut",
        "district": "Bagalkot",
        "mandi_name": "Bagalkot APMC",
        "modal_prices": [5650, 5710, 5780, 5820, 5890, 5980, 6070, 6010],
        "spread": 320,
    },
    {
        "crop_name": "Paddy",
        "district": "Mysuru",
        "mandi_name": "Mysuru APMC",
        "modal_prices": [2240, 2280, 2260, 2310, 2350, 2390, 2370, 2420],
        "spread": 140,
    },
    {
        "crop_name": "Tomato",
        "district": "Mysuru",
        "mandi_name": "Mysuru APMC",
        "modal_prices": [1450, 1620, 1380, 1710, 1980, 2440, 2210, 2050],
        "spread": 280,
    },
    {
        "crop_name": "Onion",
        "district": "Mysuru",
        "mandi_name": "Mysuru APMC",
        "modal_prices": [1760, 1820, 1910, 2050, 2180, 2340, 2290, 2140],
        "spread": 210,
    },
    {
        "crop_name": "Maize",
        "district": "Belagavi",
        "mandi_name": "Belagavi APMC",
        "modal_prices": [1930, 1950, 1940, 1970, 1990, 2010, 2030, 2050],
        "spread": 95,
    },
    {
        "crop_name": "Groundnut",
        "district": "Belagavi",
        "mandi_name": "Belagavi APMC",
        "modal_prices": [5520, 5600, 5670, 5750, 5840, 5920, 6000, 5950],
        "spread": 300,
    },
    {
        "crop_name": "Tomato",
        "district": "Belagavi",
        "mandi_name": "Belagavi APMC",
        "modal_prices": [1220, 1360, 1180, 1490, 1730, 2140, 1960, 1810],
        "spread": 250,
    },
]

WEEKLY_SNAPSHOT_DATES = [
    date(2026, 3, 7),
    date(2026, 3, 14),
    date(2026, 3, 21),
    date(2026, 3, 28),
    date(2026, 4, 4),
    date(2026, 4, 11),
    date(2026, 4, 18),
    date(2026, 4, 25),
]


def build_seed_mandi_prices() -> list[dict]:
    records = []
    for market_series in WEEKLY_MARKET_SERIES:
        for snapshot_date, modal_price in zip(WEEKLY_SNAPSHOT_DATES, market_series["modal_prices"]):
            spread = market_series["spread"]
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
