# tests/test_ai_information_coordinator.py
# NOTE: ASCII only.
from types import SimpleNamespace

import backend.services.ai_information_coordinator as aic


class _DummyResponse:
    def __init__(self, text: str, status_code: int = 200):
        self.text = text
        self.status_code = status_code


class _DummyRequests:
    def __init__(self, response: _DummyResponse):
        self.response = response
        self.calls = 0

    def get(self, *_args, **_kwargs):
        self.calls += 1
        return self.response


def _install_dummy_feed(monkeypatch, entries):
    dummy_feed = SimpleNamespace(entries=entries)

    class _FeedParser:
        @staticmethod
        def parse(_text):
            return dummy_feed

    monkeypatch.setattr(aic, "feedparser", _FeedParser, raising=False)


def test_fetch_feed_parses_entries(monkeypatch):
    aic._reset_state()
    aic.REQUEST_INTERVAL_SEC = 0

    dummy_requests = _DummyRequests(_DummyResponse("<xml/>"))
    monkeypatch.setattr(aic, "requests", dummy_requests, raising=False)
    _install_dummy_feed(
        monkeypatch,
        [
            {
                "title": "Port of Halifax expansion",
                "link": "https://example.test/ports",
                "published": "2024-01-01T00:00:00Z",
                "summary": "Port news update.",
                "tags": [{"term": "ports"}],
            }
        ],
    )

    source = aic.SourceSpec(
        name="Port of Halifax",
        feed_url="https://feeds.example.test",
        region="nova_scotia",
        category="ports",
    )
    items = aic.fetch_feed(source)
    assert len(items) == 1
    assert items[0].title == "Port of Halifax expansion"
    assert items[0].category == "ports"


def test_caching_prevents_duplicate_fetch(monkeypatch):
    aic._reset_state()
    aic.REQUEST_INTERVAL_SEC = 0

    dummy_requests = _DummyRequests(_DummyResponse("<xml/>"))
    monkeypatch.setattr(aic, "requests", dummy_requests, raising=False)
    _install_dummy_feed(
        monkeypatch,
        [
            {
                "title": "Trucking update",
                "link": "https://example.test/trucking",
                "published": "2024-01-01T00:00:00Z",
            }
        ],
    )

    source = aic.SourceSpec(
        name="TruckNews",
        feed_url="https://feeds.example.test/truck",
        region="national",
        category="trucking",
    )
    first = aic.fetch_feed(source)
    second = aic.fetch_feed(source)
    assert len(first) == 1
    assert len(second) == 1
    assert dummy_requests.calls == 1


def test_categorization_keywords():
    source = aic.SourceSpec(
        name="Canadian Shipper",
        feed_url=None,
        region="national",
        category="industry",
    )
    category = aic._categorize("Rail safety update", source, "Rail corridor project")
    assert category == "railways"


def test_filtering_by_region_and_category(monkeypatch):
    items = [
        aic.NewsItem(
            source="Port of Vancouver",
            title="BC ports update",
            url="https://example.test",
            published_at="2024-01-01T00:00:00Z",
            tags=[],
            category="ports",
            region="british_columbia",
            raw_excerpt="",
        ),
        aic.NewsItem(
            source="TruckNews",
            title="Ontario trucking update",
            url="https://example.test/2",
            published_at="2024-01-01T00:00:00Z",
            tags=[],
            category="trucking",
            region="ontario",
            raw_excerpt="",
        ),
    ]

    monkeypatch.setattr(aic, "get_canadian_logistics_news", lambda: items)
    filtered = aic.get_filtered_canadian_news(province="ontario", category="trucking")
    assert filtered["count"] == 1
    assert filtered["items"][0].region == "ontario"


def test_mock_only_integration(monkeypatch):
    aic._reset_state()
    aic.REQUEST_INTERVAL_SEC = 0

    dummy_requests = _DummyRequests(_DummyResponse("<xml/>"))
    monkeypatch.setattr(aic, "requests", dummy_requests, raising=False)
    _install_dummy_feed(
        monkeypatch,
        [
            {
                "title": "Government transport update",
                "link": "https://example.test/gov",
                "published": "2024-01-01T00:00:00Z",
            }
        ],
    )

    items = aic.get_canadian_logistics_news()
    assert items
    assert isinstance(items[0], aic.NewsItem)
