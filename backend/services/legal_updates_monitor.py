from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from html.parser import HTMLParser

import httpx

from backend.services.portal_requests_store import create_admin_notification

logger = logging.getLogger("legal_updates_monitor")

DEFAULT_SOURCES = [
    "https://www.ccmta.ca/en/",
    "https://www.canada.ca/en/transportation-agency.html",
    "https://tc.canada.ca/en",
    "https://www.cbsa-asfc.gc.ca/menu-eng.html",
]

CACHE_PATH = os.path.join("logs", "legal_updates_cache.json")

BOT_LABELS = {
    "information_coordinator": "Information Coordinator",
    "legal_bot": "AI Legal Consultant",
    "safety_manager": "Safety Manager",
    "freight_broker": "MapleLoad Canada",
    "general_manager": "Executive Command Center",
}

BOT_KEYWORDS = {
    "legal_bot": [
        "regulation",
        "act",
        "legislation",
        "compliance",
        "policy",
        "tariff",
        "agreement",
        "enforcement",
        "licensing",
        "certificate",
    ],
    "safety_manager": [
        "safety",
        "inspection",
        "hazard",
        "compliance",
        "emergency",
        "risk",
        "incident",
        "security",
    ],
    "freight_broker": [
        "freight",
        "transport",
        "trucking",
        "carrier",
        "shipping",
        "cargo",
        "border",
        "customs",
    ],
    "information_coordinator": [
        "update",
        "news",
        "announcement",
        "advisory",
    ],
    "general_manager": [
        "policy",
        "strategy",
        "governance",
        "minister",
        "agency",
    ],
}


class _SimpleHtmlParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.in_title = False
        self.in_heading = False
        self.title = ""
        self.headings: List[str] = []
        self.links: List[Dict[str, str]] = []
        self._current_href: Optional[str] = None

    def handle_starttag(self, tag: str, attrs):
        if tag == "title":
            self.in_title = True
        if tag in ("h1", "h2", "h3"):
            self.in_heading = True
        if tag == "a":
            href = None
            for k, v in attrs:
                if k == "href":
                    href = v
                    break
            self._current_href = href

    def handle_endtag(self, tag: str):
        if tag == "title":
            self.in_title = False
        if tag in ("h1", "h2", "h3"):
            self.in_heading = False
        if tag == "a":
            self._current_href = None

    def handle_data(self, data: str):
        text = (data or "").strip()
        if not text:
            return
        if self.in_title:
            if not self.title:
                self.title = text
        if self.in_heading:
            if text not in self.headings:
                self.headings.append(text)
        if self._current_href:
            if len(text) > 3 and len(self.links) < 25:
                self.links.append({"text": text, "href": self._current_href})


def _load_cache() -> Dict[str, str]:
    if not os.path.exists(CACHE_PATH):
        return {}
    try:
        with open(CACHE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _save_cache(cache: Dict[str, str]) -> None:
    os.makedirs(os.path.dirname(CACHE_PATH), exist_ok=True)
    with open(CACHE_PATH, "w", encoding="utf-8") as f:
        json.dump(cache, f, indent=2, sort_keys=True)


def _hash_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="ignore")).hexdigest()


def _categorize_update(text: str) -> List[str]:
    text_lower = text.lower()
    matched: List[str] = []
    for bot_key, keywords in BOT_KEYWORDS.items():
        if any(k in text_lower for k in keywords):
            matched.append(bot_key)
    if "information_coordinator" not in matched:
        matched.append("information_coordinator")
    return matched


def _build_update_summary(parsed: _SimpleHtmlParser, url: str) -> str:
    parts = []
    if parsed.title:
        parts.append(parsed.title)
    if parsed.headings:
        parts.extend(parsed.headings[:3])
    if not parts:
        parts.append(url)
    return " | ".join(parts)


def _render_bot_sections(assignments: Dict[str, List[str]]) -> str:
    lines: List[str] = []
    for bot_key, items in assignments.items():
        label = BOT_LABELS.get(bot_key, bot_key)
        if not items:
            continue
        lines.append(f"{label}:")
        for item in items[:8]:
            lines.append(f"- {item}")
        lines.append("")
    return "\n".join(lines).strip()


def _build_notification_message(
    updates: List[Dict[str, str]],
    assignments: Dict[str, List[str]],
) -> str:
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    header = [
        "Daily regulatory scan completed.",
        f"Timestamp: {timestamp}",
        "Sources:",
    ]
    for update in updates:
        header.append(f"- {update['url']}")
    header.append("")
    header.append("Bot briefs:")
    header.append(_render_bot_sections(assignments) or "No categorized updates.")
    return "\n".join(header).strip()


def _next_run_delay(target_hour: int, target_minute: int) -> float:
    now = datetime.now()
    target = now.replace(hour=target_hour, minute=target_minute, second=0, microsecond=0)
    if target <= now:
        target = target + timedelta(days=1)
    return max(30.0, (target - now).total_seconds())


def _parse_time_hhmm(value: str, default: str = "08:00") -> tuple[int, int]:
    raw = (value or "").strip() or default
    try:
        parts = raw.split(":")
        hour = int(parts[0])
        minute = int(parts[1]) if len(parts) > 1 else 0
        hour = min(max(hour, 0), 23)
        minute = min(max(minute, 0), 59)
        return hour, minute
    except Exception:
        return (8, 0)


def _assign_updates_to_bots(updates: List[Dict[str, str]]) -> Dict[str, List[str]]:
    assignments: Dict[str, List[str]] = {k: [] for k in BOT_LABELS.keys()}
    for update in updates:
        summary = update.get("summary") or update.get("url") or ""
        categories = _categorize_update(summary)
        for cat in categories:
            if cat in assignments:
                assignments[cat].append(summary)
    return assignments


async def _fetch_source(url: str) -> Optional[Dict[str, str]]:
    try:
        async with httpx.AsyncClient(timeout=20) as client:
            resp = await client.get(url, headers={"User-Agent": "GTS-Legal-Monitor/1.0"})
            resp.raise_for_status()
            html = resp.text or ""
    except Exception as exc:
        logger.warning("fetch failed for %s: %s", url, exc)
        return None

    parser = _SimpleHtmlParser()
    try:
        parser.feed(html)
    except Exception:
        pass

    summary = _build_update_summary(parser, url)
    return {
        "url": url,
        "title": parser.title or url,
        "summary": summary,
    }


async def run_legal_updates_scan(
    sources: Optional[List[str]] = None,
) -> Dict[str, object]:
    sources = sources or DEFAULT_SOURCES
    cache = _load_cache()

    results: List[Dict[str, str]] = []
    updates: List[Dict[str, str]] = []

    for url in sources:
        parsed = await _fetch_source(url)
        if not parsed:
            continue
        results.append(parsed)

        signature = _hash_text(parsed.get("summary") or parsed.get("title") or url)
        if cache.get(url) != signature:
            cache[url] = signature
            updates.append(parsed)

    if results:
        _save_cache(cache)

    assignments = _assign_updates_to_bots(updates if updates else results)
    message = _build_notification_message(results, assignments)
    title = f"Daily legal updates - {datetime.utcnow().strftime('%Y-%m-%d')}"

    try:
        await create_admin_notification(
            request_id=None,
            notification_type="legal_updates",
            title=title,
            message=message,
        )
    except Exception as exc:
        logger.warning("create_admin_notification failed: %s", exc)

    return {
        "sources": results,
        "updates": updates,
        "assignments": assignments,
    }


async def legal_updates_scheduler_loop() -> None:
    schedule_time = os.getenv("LEGAL_UPDATES_TIME", "08:00")
    hour, minute = _parse_time_hhmm(schedule_time)
    logger.info("legal updates scheduler active at %02d:%02d", hour, minute)

    while True:
        delay = _next_run_delay(hour, minute)
        await asyncio.sleep(delay)
        try:
            await run_legal_updates_scan()
        except Exception as exc:
            logger.warning("legal updates scan failed: %s", exc)
