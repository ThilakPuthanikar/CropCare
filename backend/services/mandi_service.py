import logging
import re
from datetime import datetime, timezone
from html import unescape
from html.parser import HTMLParser
from typing import Optional

import requests

logger = logging.getLogger(__name__)

KARNATAKA_MANDI_SOURCE_URL = "https://krama.karnataka.gov.in/Reports/Main_rep"

REQUEST_TIMEOUT_SECONDS = 45
USER_AGENT = "CropCare/1.0"

HEADER_ALIASES = {
    "commodity": "crop_name",
    "crop": "crop_name",
    "variety": "variety",
    "grade": "grade",
    "district": "district",
    "market": "mandi_name",
    "market name": "mandi_name",
    "mandi": "mandi_name",
    "arrival": "arrival",
    "arrivals": "arrival",
    "unit": "unit",
    "min price": "min_price",
    "minimum price": "min_price",
    "max price": "max_price",
    "maximum price": "max_price",
    "modal price": "price_per_quintal",
    "model price": "price_per_quintal",
}

REQUIRED_FIELDS = {"crop_name", "mandi_name", "min_price", "max_price", "price_per_quintal"}


def _clean_text(value: Optional[str]) -> str:
    if value is None:
        return ""
    cleaned = unescape(value)
    cleaned = re.sub(r"\s+", " ", cleaned.replace("\xa0", " ")).strip()
    return cleaned


def _normalize_header(value: str) -> Optional[str]:
    normalized = _clean_text(value).lower()
    normalized = re.sub(r"[^a-z0-9]+", " ", normalized).strip()
    return HEADER_ALIASES.get(normalized)


def _parse_float(value: Optional[str]) -> Optional[float]:
    cleaned = _clean_text(value)
    if not cleaned:
        return None
    cleaned = cleaned.replace(",", "")
    match = re.search(r"-?\d+(?:\.\d+)?", cleaned)
    if not match:
        return None
    try:
        return float(match.group(0))
    except ValueError:
        return None


class _HTMLTableExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.tables: list[list[list[tuple[str, str]]]] = []
        self._table_stack: list[list[list[tuple[str, str]]]] = []
        self._row_stack: list[list[tuple[str, str]]] = []
        self._cell_text_parts: list[str] = []
        self._current_cell_tag: Optional[str] = None

    def handle_starttag(self, tag: str, attrs) -> None:
        lowered = tag.lower()
        if lowered == "table":
            self._table_stack.append([])
        elif lowered == "tr" and self._table_stack:
            self._row_stack.append([])
        elif lowered in {"th", "td"} and self._row_stack:
            self._current_cell_tag = lowered
            self._cell_text_parts = []
        elif lowered == "br" and self._current_cell_tag:
            self._cell_text_parts.append(" ")

    def handle_data(self, data: str) -> None:
        if self._current_cell_tag:
            self._cell_text_parts.append(data)

    def handle_endtag(self, tag: str) -> None:
        lowered = tag.lower()
        if lowered in {"th", "td"} and self._current_cell_tag == lowered and self._row_stack:
            text = _clean_text("".join(self._cell_text_parts))
            self._row_stack[-1].append((lowered, text))
            self._current_cell_tag = None
            self._cell_text_parts = []
        elif lowered == "tr" and self._row_stack and self._table_stack:
            row = self._row_stack.pop()
            if any(text for _, text in row):
                self._table_stack[-1].append(row)
        elif lowered == "table" and self._table_stack:
            table = self._table_stack.pop()
            if table:
                self.tables.append(table)


def _extract_tables(html: str) -> list[list[list[tuple[str, str]]]]:
    parser = _HTMLTableExtractor()
    parser.feed(html)
    parser.close()
    return parser.tables


def _build_header_index(row: list[tuple[str, str]]) -> dict[str, int]:
    header_index: dict[str, int] = {}
    for idx, (_, text) in enumerate(row):
        normalized = _normalize_header(text)
        if normalized and normalized not in header_index:
            header_index[normalized] = idx
    return header_index


def _pick_source_table(tables: list[list[list[tuple[str, str]]]]) -> tuple[list[list[tuple[str, str]]], dict[str, int]]:
    best_match: Optional[tuple[list[list[tuple[str, str]]], dict[str, int]]] = None
    best_score = -1

    for table in tables:
        if not table:
            continue
        header_index = _build_header_index(table[0])
        score = len(REQUIRED_FIELDS.intersection(header_index.keys()))
        if score > best_score:
            best_score = score
            best_match = (table, header_index)

    if not best_match or best_score < len(REQUIRED_FIELDS):
        raise ValueError("Unable to locate a mandi price table with the expected columns on the Karnataka source page.")

    return best_match


def _extract_price_date(html: str, fetched_at: datetime) -> datetime.date:
    match = re.search(r"(?:as on|report date|date)\s*[:\-]?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})", html, re.IGNORECASE)
    if match:
        raw_value = match.group(1)
        for fmt in ("%d/%m/%Y", "%d-%m-%Y", "%d/%m/%y", "%d-%m-%y"):
            try:
                return datetime.strptime(raw_value, fmt).date()
            except ValueError:
                continue
    return fetched_at.date()


def _normalize_row(
    row: list[tuple[str, str]],
    header_index: dict[str, int],
    price_date,
    fetched_at: datetime,
) -> Optional[dict]:
    values = [text for _, text in row]

    def get_value(field: str) -> str:
        index = header_index.get(field)
        if index is None or index >= len(values):
            return ""
        return values[index]

    modal_price = _parse_float(get_value("price_per_quintal"))
    min_price = _parse_float(get_value("min_price"))
    max_price = _parse_float(get_value("max_price"))
    crop_name = _clean_text(get_value("crop_name"))
    mandi_name = _clean_text(get_value("mandi_name"))
    if not crop_name or not mandi_name or modal_price is None:
        return None

    district = _clean_text(get_value("district")) or "Unknown"
    return {
        "crop_name": crop_name,
        "variety": _clean_text(get_value("variety")) or None,
        "grade": _clean_text(get_value("grade")) or None,
        "district": district,
        "mandi_name": mandi_name,
        "arrival": _parse_float(get_value("arrival")),
        "unit": _clean_text(get_value("unit")) or None,
        "price_per_quintal": modal_price,
        "min_price": min_price,
        "max_price": max_price,
        "price_date": price_date,
        "last_updated": fetched_at,
    }


def fetch_karnataka_mandi_prices() -> dict:
    """Fetch Karnataka mandi prices using standard HTTP requests and stdlib HTML parsing.

    Uses the existing _HTMLTableExtractor, _pick_source_table, and _normalize_row
    functions already defined in this module — no external scraping dependencies needed.
    """
    fetched_at = datetime.now(timezone.utc)
    logger.info("Fetching Karnataka mandi prices via HTTP: %s", KARNATAKA_MANDI_SOURCE_URL)

    try:
        with requests.Session() as session:
            session.trust_env = False
            response = session.get(
                KARNATAKA_MANDI_SOURCE_URL,
                timeout=REQUEST_TIMEOUT_SECONDS,
                headers={
                    "User-Agent": USER_AGENT,
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                    "Accept-Language": "en-US,en;q=0.5",
                },
            )
        response.raise_for_status()
        html = response.text

        tables = _extract_tables(html)
        if not tables:
            raise ValueError("No HTML tables found on the Karnataka mandi source page.")

        source_table, header_index = _pick_source_table(tables)
        price_date = _extract_price_date(html, fetched_at)

        records = []
        for row in source_table[1:]:
            normalized = _normalize_row(row, header_index, price_date, fetched_at)
            if normalized:
                records.append(normalized)

        if not records:
            raise ValueError("Parsing completed but yielded 0 valid mandi price rows.")

        logger.info("Successfully extracted %s mandi price records.", len(records))
        return {
            "source_url": KARNATAKA_MANDI_SOURCE_URL,
            "fetched_at": fetched_at,
            "row_count": len(records),
            "records": records,
            "method": "http_stdlib",
        }

    except Exception as exc:
        logger.exception("Karnataka mandi scrape failed: %s", exc)
        raise

