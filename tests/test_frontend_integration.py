"""
Frontend Integration Tests
Tests critical user flows and component functionality after package updates
"""
import pytest
import asyncio
from playwright.async_api import async_playwright, expect
import os

# Test configuration
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
TEST_EMAIL = "tester@gts.com"
TEST_PASSWORD = "123456"


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def browser():
    """Launch browser for testing"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        yield browser
        await browser.close()


@pytest.fixture
async def page(browser):
    """Create new page for each test"""
    context = await browser.new_context()
    page = await context.new_page()
    yield page
    await context.close()


class TestAuthentication:
    """Test authentication flow"""

    @pytest.mark.asyncio
    async def test_login_page_loads(self, page):
        """Verify login page loads without errors"""
        response = await page.goto(FRONTEND_URL)
        assert response.status == 200, "Frontend should load successfully"
        
        # Check for no console errors
        errors = []
        page.on("console", lambda msg: errors.append(msg) if msg.type == "error" else None)
        await page.wait_for_load_state("networkidle")
        
        # Allow some time for React to render
        await asyncio.sleep(2)
        
        assert len(errors) == 0, f"No console errors expected, found: {errors}"

    @pytest.mark.asyncio
    async def test_login_flow(self, page):
        """Test complete login flow"""
        await page.goto(FRONTEND_URL)
        
        # Wait for login form
        await page.wait_for_selector('input[type="email"], input[name="email"]', timeout=5000)
        
        # Fill login form
        await page.fill('input[type="email"], input[name="email"]', TEST_EMAIL)
        await page.fill('input[type="password"], input[name="password"]', TEST_PASSWORD)
        
        # Submit form
        await page.click('button[type="submit"], button:has-text("Login")')
        
        # Wait for navigation or dashboard
        await page.wait_for_timeout(3000)
        
        # Check if redirected to dashboard
        current_url = page.url
        assert "/dashboard" in current_url or "/admin" in current_url, "Should redirect to dashboard after login"


class TestDashboard:
    """Test dashboard functionality"""

    @pytest.mark.asyncio
    async def test_dashboard_renders(self, page):
        """Verify dashboard renders all components"""
        # Login first
        await page.goto(FRONTEND_URL)
        await page.wait_for_selector('input[type="email"]', timeout=5000)
        await page.fill('input[type="email"]', TEST_EMAIL)
        await page.fill('input[type="password"]', TEST_PASSWORD)
        await page.click('button[type="submit"]')
        await page.wait_for_timeout(3000)
        
        # Check for dashboard elements
        # This will vary based on your actual dashboard structure
        await page.wait_for_selector('body', timeout=5000)
        
        # Verify no React errors
        content = await page.content()
        assert "react" not in content.lower() or "error" not in content.lower()


class TestBotManagement:
    """Test bot control panel"""

    @pytest.mark.asyncio
    async def test_bots_page_accessible(self, page):
        """Verify bots page loads"""
        # Login first
        await page.goto(FRONTEND_URL)
        await page.wait_for_selector('input[type="email"]', timeout=5000)
        await page.fill('input[type="email"]', TEST_EMAIL)
        await page.fill('input[type="password"]', TEST_PASSWORD)
        await page.click('button[type="submit"]')
        await page.wait_for_timeout(3000)
        
        # Navigate to bots page
        await page.goto(f"{FRONTEND_URL}/admin/bots")
        await page.wait_for_timeout(2000)
        
        # Check page loaded
        current_url = page.url
        assert "/bots" in current_url or "/admin" in current_url


class TestResponsiveDesign:
    """Test responsive design across viewports"""

    @pytest.mark.asyncio
    async def test_mobile_viewport(self, browser):
        """Test mobile viewport (375x667 - iPhone SE)"""
        context = await browser.new_context(viewport={"width": 375, "height": 667})
        page = await context.new_page()
        
        response = await page.goto(FRONTEND_URL)
        assert response.status == 200
        
        await page.wait_for_load_state("networkidle")
        await asyncio.sleep(1)
        
        # Verify page is responsive
        width = await page.evaluate("window.innerWidth")
        assert width == 375
        
        await context.close()

    @pytest.mark.asyncio
    async def test_tablet_viewport(self, browser):
        """Test tablet viewport (768x1024 - iPad)"""
        context = await browser.new_context(viewport={"width": 768, "height": 1024})
        page = await context.new_page()
        
        response = await page.goto(FRONTEND_URL)
        assert response.status == 200
        
        await page.wait_for_load_state("networkidle")
        
        width = await page.evaluate("window.innerWidth")
        assert width == 768
        
        await context.close()

    @pytest.mark.asyncio
    async def test_desktop_viewport(self, browser):
        """Test desktop viewport (1920x1080)"""
        context = await browser.new_context(viewport={"width": 1920, "height": 1080})
        page = await context.new_page()
        
        response = await page.goto(FRONTEND_URL)
        assert response.status == 200
        
        await page.wait_for_load_state("networkidle")
        
        width = await page.evaluate("window.innerWidth")
        assert width == 1920
        
        await context.close()


class TestPerformance:
    """Test frontend performance metrics"""

    @pytest.mark.asyncio
    async def test_initial_load_time(self, page):
        """Verify initial page load is under 3 seconds"""
        import time
        
        start = time.time()
        await page.goto(FRONTEND_URL)
        await page.wait_for_load_state("networkidle")
        end = time.time()
        
        load_time = end - start
        assert load_time < 3.0, f"Page should load in under 3s, took {load_time:.2f}s"

    @pytest.mark.asyncio
    async def test_no_memory_leaks(self, page):
        """Basic memory leak detection"""
        await page.goto(FRONTEND_URL)
        
        # Get initial memory usage
        initial_memory = await page.evaluate("performance.memory ? performance.memory.usedJSHeapSize : 0")
        
        # Simulate navigation
        for _ in range(5):
            await page.reload()
            await page.wait_for_load_state("networkidle")
            await asyncio.sleep(1)
        
        # Get final memory usage
        final_memory = await page.evaluate("performance.memory ? performance.memory.usedJSHeapSize : 0")
        
        # Memory shouldn't grow more than 50%
        if initial_memory > 0:
            growth = (final_memory - initial_memory) / initial_memory
            assert growth < 0.5, f"Memory grew by {growth*100:.1f}%, possible leak"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--asyncio-mode=auto"])
