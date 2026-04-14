"""Frontend integration smoke tests gated on a live frontend server."""

import os
from urllib.request import urlopen

import pytest

playwright_async = pytest.importorskip(
    "playwright.async_api",
    reason="playwright is optional for frontend integration tests",
)
async_playwright = playwright_async.async_playwright

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")


def _frontend_available() -> bool:
    try:
        with urlopen(FRONTEND_URL, timeout=3) as response:
            return 200 <= getattr(response, "status", 0) < 500
    except Exception:
        return False


def _require_frontend() -> None:
    if not _frontend_available():
        pytest.skip(f"Frontend not reachable at {FRONTEND_URL}")


@pytest.fixture
async def browser():
    _require_frontend()
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        try:
            yield browser
        finally:
            await browser.close()


@pytest.fixture
async def page(browser):
    context = await browser.new_context()
    page = await context.new_page()
    try:
        yield page
    finally:
        await context.close()


@pytest.mark.asyncio
async def test_frontend_homepage_loads(page):
    response = await page.goto(FRONTEND_URL)
    assert response is not None
    assert response.status == 200


@pytest.mark.asyncio
async def test_frontend_mobile_viewport(browser):
    context = await browser.new_context(viewport={"width": 375, "height": 667})
    page = await context.new_page()
    try:
        response = await page.goto(FRONTEND_URL)
        assert response is not None
        assert response.status == 200
        width = await page.evaluate("window.innerWidth")
        assert width == 375
    finally:
        await context.close()
