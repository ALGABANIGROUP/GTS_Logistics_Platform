from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

try:
    import requests
except Exception:
    requests = None

try:
    from bs4 import BeautifulSoup  # type: ignore
except Exception:
    BeautifulSoup = None  # type: ignore

try:
    import feedparser  # type: ignore
except Exception:
    feedparser = None  # type: ignore

REQUEST_INTERVAL_SEC = 1.5


@dataclass
class SourceSpec:
    name: str
    feed_url: Optional[str]
    region: str
    category: str


@dataclass
class NewsItem:
    source: str
    title: str
    url: str
    published_at: str
    tags: List[str]
    category: str
    region: str
    raw_excerpt: str


@dataclass
class CacheItem:
    value: Any
    expires_at: float


class TTLCache:
    def __init__(self, ttl_seconds: int = 3600, max_items: int = 256) -> None:
        self.ttl_seconds = ttl_seconds
        self.max_items = max_items
        self._store: Dict[str, CacheItem] = {}

    def get(self, key: str) -> Optional[Any]:
        item = self._store.get(key)
        if not item:
            return None
        if time.time() >= item.expires_at:
            self._store.pop(key, None)
            return None
        return item.value

    def set(self, key: str, value: Any) -> None:
        if len(self._store) >= self.max_items:
            now = time.time()
            expired = [k for k, v in self._store.items() if now >= v.expires_at]
            for k in expired:
                self._store.pop(k, None)
            if len(self._store) >= self.max_items:
                self._store.pop(next(iter(self._store.keys())), None)
        self._store[key] = CacheItem(value=value, expires_at=time.time() + self.ttl_seconds)

    def clear(self) -> None:
        self._store.clear()


class CanadianNewsScraper:
    def __init__(self, request_delay: float = 1.5, ttl_seconds: int = 3600) -> None:
        self.request_delay = request_delay
        self.last_request_time: Dict[str, float] = {}
        self.cache = TTLCache(ttl_seconds=ttl_seconds, max_items=256)

        self.sources: Dict[str, str] = {
            "statscan": "https://www150.statcan.gc.ca/n1/daily-quotidien/",
            "transport_canada": "https://tc.canada.ca/en/news",
            "todays_trucking": "https://www.todaystrucking.com/",
            "truck_news_canada": "https://www.trucknewscanada.com/",
            "canadian_shipper": "https://www.canadianshipper.com/",
            "trucking_hr": "https://truckinghr.com/news/",
            "globe_transport": "https://www.theglobeandmail.com/business/industry-news/transportation/",
            "financial_post_transport": "https://financialpost.com/category/transportation/",
            "bnn_transport": "https://www.bnnbloomberg.ca/markets/transportation",
            "ontario_trucking_assoc": "https://ontruck.org/news/",
            "alberta_motor_transport": "https://amta.ca/news/",
            "bc_trucking_assoc": "https://www.bctrucking.com/news/",
            "port_vancouver": "https://www.portvancouver.com/news/",
            "port_montreal": "https://www.port-montreal.com/en/news",
            "port_halifax": "https://www.portofhalifax.ca/news/",
            "cn_rail": "https://www.cn.ca/en/news/",
            "cp_rail": "https://www.cpr.ca/en/media",
        }

        self.selectors_by_source: Dict[str, List[str]] = {
            "statscan": ["h3", "h2", "a"],
            "transport_canada": ["h3", "h2", ".title", "[class*='title']"],
            "todays_trucking": ["h2", "h3", ".entry-title", "[class*='title']"],
            "truck_news_canada": ["h2", "h3", ".entry-title", "[class*='title']"],
            "canadian_shipper": ["h2", "h3", ".entry-title", "[class*='title']"],
            "trucking_hr": ["h3", "h2", ".news-title", "[class*='title']"],
            "globe_transport": ["h3", ".c-headline", "[class*='headline']", "a"],
            "financial_post_transport": ["h3", ".article-card__headline", "[class*='headline']", "a"],
            "bnn_transport": ["h3", ".story-card__headline", "[class*='headline']", "a"],
            "ontario_trucking_assoc": ["h3", "h2", ".news-title", "[class*='title']"],
            "alberta_motor_transport": ["h2", "h3", ".post-title", "[class*='title']"],
            "bc_trucking_assoc": ["h3", "h2", ".article-title", "[class*='title']"],
            "port_vancouver": ["h3", "h2", ".news-title", "[class*='title']"],
            "port_montreal": ["h2", "h3", ".news-item-title", "[class*='title']"],
            "port_halifax": ["h3", "h2", ".post-title", "[class*='title']"],
            "cn_rail": ["h3", "h2", ".news-title", "[class*='title']"],
            "cp_rail": ["h3", "h2", ".media-title", "[class*='title']"],
        }

        self.default_headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0 Safari/537.36"
            )
        }

    def reset_state(self) -> None:
        self.last_request_time.clear()
        self.cache.clear()

    def _rate_limit(self, source_name: str) -> None:
        last = self.last_request_time.get(source_name)
        if last is None:
            return
        elapsed = time.time() - last
        if elapsed < self.request_delay:
            time.sleep(self.request_delay - elapsed)

    def scrape_source(self, source_name: str, url: str, max_titles: int = 5) -> List[str]:
        if requests is None:
            return [f"[{source_name}] requests is not installed."]
        if BeautifulSoup is None:
            return [f"[{source_name}] beautifulsoup4 is not installed."]

        cache_key = f"news::{source_name}"
        cached = self.cache.get(cache_key)
        if isinstance(cached, list) and cached:
            return cached[:max_titles]

        self._rate_limit(source_name)

        try:
            res = requests.get(url, headers=self.default_headers, timeout=12)
            res.raise_for_status()
            soup = BeautifulSoup(res.text, "html.parser")

            selectors = self.selectors_by_source.get(source_name) or ["h3", "h2", "h1", "a"]
            titles: List[str] = []

            for selector in selectors:
                for el in soup.select(selector):
                    text = el.get_text(" ", strip=True)
                    if not text:
                        continue
                    if len(text) < 25 or len(text) > 220:
                        continue
                    if text in titles:
                        continue
                    titles.append(text)
                    if len(titles) >= 10:
                        break
                if titles:
                    break

            self.last_request_time[source_name] = time.time()

            if not titles:
                titles = [f"[{source_name}] No titles found."]

            self.cache.set(cache_key, titles)
            return titles[:max_titles]

        except Exception as exc:
            self.last_request_time[source_name] = time.time()
            err = f"[{source_name}] error: {exc}"
            self.cache.set(cache_key, [err])
            return [err]

    def get_canadian_logistics_news(self) -> List[str]:
        results: List[str] = []
        for source_name, url in self.sources.items():
            titles = self.scrape_source(source_name, url, max_titles=5)
            for title in titles:
                if title.startswith("["):
                    results.append(title)
                else:
                    results.append(f"[{source_name.upper()}] {title}")
        return results

    def organize_news_by_category(self, news_items: List[str]) -> Dict[str, List[str]]:
        categories: Dict[str, List[str]] = {
            "government": [],
            "trucking": [],
            "ports": [],
            "railways": [],
            "industry": [],
            "regional": [],
            "international": [],
            "errors": [],
        }

        for item in news_items:
            lowered = item.lower()
            if "error:" in lowered or "requests" in lowered:
                categories["errors"].append(item)
            elif any(k in lowered for k in ["statscan", "transport_canada", "transport canada"]):
                categories["government"].append(item)
            elif any(k in lowered for k in ["trucking", "todays_trucking", "truck_news", "canadian_shipper", "freight", "truck"]):
                categories["trucking"].append(item)
            elif "port_" in lowered or "port" in lowered:
                categories["ports"].append(item)
            elif any(k in lowered for k in ["rail", "railway", "cn_rail", "cp_rail"]):
                categories["railways"].append(item)
            elif any(k in lowered for k in ["manufacturer", "retail", "industry", "supply"]):
                categories["industry"].append(item)
            elif any(k in lowered for k in ["ontario", "alberta", "british columbia", "vancouver", "montreal", "bc_"]):
                categories["regional"].append(item)
            else:
                categories["trucking"].append(item)

        return categories

    def get_comprehensive_canadian_logistics_news(self) -> Dict[str, List[str]]:
        all_results = self.get_canadian_logistics_news()
        return self.organize_news_by_category(all_results)

    def get_filtered_canadian_news(
        self,
        province: Optional[str] = None,
        category: Optional[str] = None,
        keywords: Optional[str] = None,
    ) -> Dict[str, Any]:
        all_news = self.get_comprehensive_canadian_logistics_news()

        if category and category in all_news:
            return {"filtered_results": all_news[category], "count": len(all_news[category])}

        filtered: List[str] = []

        if province:
            province = province.lower().strip()
            province_keywords = {
                "ontario": ["ontario", "toronto", "ottawa", "mississauga"],
                "quebec": ["quebec", "montreal", "quebec city"],
                "british_columbia": ["british columbia", "vancouver", "bc "],
                "alberta": ["alberta", "calgary", "edmonton"],
                "manitoba": ["manitoba", "winnipeg"],
                "saskatchewan": ["saskatchewan", "regina", "saskatoon"],
            }
            keys = province_keywords.get(province, [province])
            for items in all_news.values():
                for item in items:
                    if any(k in item.lower() for k in keys):
                        filtered.append(item)

            return {"filtered_results": filtered, "count": len(filtered)}

        if keywords:
            keys = [k.strip().lower() for k in keywords.split(",") if k.strip()]
            for items in all_news.values():
                for item in items:
                    if any(k in item.lower() for k in keys):
                        filtered.append(item)
            return {"filtered_results": filtered, "count": len(filtered)}

        return {"categorized": all_news, "count": sum(len(v) for v in all_news.values())}

    def get_daily_summary(self) -> Dict[str, Any]:
        categorized = self.get_comprehensive_canadian_logistics_news()
        all_items: List[str] = []
        for items in categorized.values():
            all_items.extend(items)

        word_freq: Dict[str, int] = {}
        for line in all_items:
            for word in line.lower().split():
                word = "".join(ch for ch in word if ch.isalnum())
                if len(word) <= 4:
                    continue
                word_freq[word] = word_freq.get(word, 0) + 1

        trending = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:7]

        return {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_sources": len(self.sources),
            "totals": {k: len(v) for k, v in categorized.items()},
            "trending_topics": [w for w, _ in trending],
            "news_by_category": {k: v[:5] for k, v in categorized.items()},
        }


_canadian_scraper_singleton: Optional[CanadianNewsScraper] = None


def get_canadian_scraper() -> CanadianNewsScraper:
    global _canadian_scraper_singleton
    if _canadian_scraper_singleton is None:
        _canadian_scraper_singleton = CanadianNewsScraper(request_delay=1.5, ttl_seconds=3600)
    return _canadian_scraper_singleton


def _reset_state() -> None:
    global _canadian_scraper_singleton
    if _canadian_scraper_singleton is not None:
        _canadian_scraper_singleton.reset_state()
    _canadian_scraper_singleton = CanadianNewsScraper(
        request_delay=REQUEST_INTERVAL_SEC,
        ttl_seconds=3600,
    )


def _categorize(title: str, source: SourceSpec, summary: str = "") -> str:
    text = f"{title} {summary} {source.name} {source.category}".lower()
    if any(term in text for term in ("rail", "railway", "corridor", "cn", "cp")):
        return "railways"
    if any(term in text for term in ("port", "harbour", "harbor", "terminal")):
        return "ports"
    if any(term in text for term in ("truck", "trucking", "freight", "carrier")):
        return "trucking"
    if any(term in text for term in ("transport canada", "government", "statscan")):
        return "government"
    return source.category or "industry"


def fetch_feed(source: SourceSpec) -> List[NewsItem]:
    if not source.feed_url:
        return []

    scraper = get_canadian_scraper()
    scraper.request_delay = REQUEST_INTERVAL_SEC
    cache_key = f"feed::{source.feed_url}"
    cached = scraper.cache.get(cache_key)
    if isinstance(cached, list):
        return cached

    if requests is None or feedparser is None:
        return []

    now = time.time()
    last_request = scraper.last_request_time.get(source.feed_url)
    if last_request and now - last_request < scraper.request_delay:
        time.sleep(scraper.request_delay - (now - last_request))

    response = requests.get(source.feed_url, headers=scraper.default_headers, timeout=12)
    if hasattr(response, "raise_for_status"):
        response.raise_for_status()

    parsed = feedparser.parse(response.text)
    items: List[NewsItem] = []
    for entry in getattr(parsed, "entries", []) or []:
        tags = [tag.get("term", "") for tag in entry.get("tags", []) if isinstance(tag, dict)]
        title = str(entry.get("title", "")).strip()
        summary = str(entry.get("summary", "") or "")
        items.append(
            NewsItem(
                source=source.name,
                title=title,
                url=str(entry.get("link", "")).strip(),
                published_at=str(entry.get("published", "") or ""),
                tags=[tag for tag in tags if tag],
                category=_categorize(title, source, summary),
                region=source.region,
                raw_excerpt=summary,
            )
        )

    scraper.last_request_time[source.feed_url] = time.time()
    scraper.cache.set(cache_key, items)
    return items


def get_canadian_logistics_news() -> List[NewsItem]:
    sources = [
        SourceSpec(
            name="Transport Canada",
            feed_url="https://tc.canada.ca/en/news/rss.xml",
            region="national",
            category="government",
        ),
        SourceSpec(
            name="Canadian Shipper",
            feed_url="https://www.canadianshipper.com/feed/",
            region="national",
            category="industry",
        ),
        SourceSpec(
            name="TruckNews",
            feed_url="https://www.trucknews.com/feed/",
            region="national",
            category="trucking",
        ),
    ]
    items: List[NewsItem] = []
    for source in sources:
        try:
            items.extend(fetch_feed(source))
        except Exception:
            continue
    return items


def get_comprehensive_canadian_logistics_news() -> Dict[str, List[NewsItem]]:
    items = get_canadian_logistics_news()
    grouped: Dict[str, List[NewsItem]] = {
        "government": [],
        "trucking": [],
        "ports": [],
        "railways": [],
        "industry": [],
        "regional": [],
        "international": [],
        "errors": [],
    }
    for item in items:
        grouped.setdefault(item.category, []).append(item)
    return grouped


def get_filtered_canadian_news(
    province: Optional[str] = None,
    category: Optional[str] = None,
    keywords: Optional[str] = None,
) -> Dict[str, Any]:
    items = get_canadian_logistics_news()
    filtered = items
    if province:
        province_norm = province.strip().lower()
        filtered = [item for item in filtered if item.region == province_norm]
    if category:
        filtered = [item for item in filtered if item.category == category]
    if keywords:
        terms = [term.strip().lower() for term in keywords.split(",") if term.strip()]
        filtered = [
            item
            for item in filtered
            if any(term in f"{item.title} {item.raw_excerpt}".lower() for term in terms)
        ]
    return {"items": filtered, "count": len(filtered)}


def get_daily_canadian_news_summary() -> Dict[str, Any]:
    return get_canadian_scraper().get_daily_summary()
