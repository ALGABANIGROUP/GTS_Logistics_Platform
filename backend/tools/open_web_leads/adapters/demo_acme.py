# backend/tools/open_web_leads/adapters/demo_acme.py

from typing import List
from datetime import datetime

import httpx
from bs4 import BeautifulSoup

from .base import BaseOpenWebLeadAdapter
from ..schemas import OpenWebLeadCreate


class DemoAcmeAdapter(BaseOpenWebLeadAdapter):
    source_name = "demo-acme-logistics.com"

    # A fictional example URL
    BASE_URL = "https://example.com/open-loads"

    async def fetch_leads(self) -> List[OpenWebLeadCreate]:
        leads: List[OpenWebLeadCreate] = []

        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(self.BASE_URL)
            resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "html.parser")

        # You will later customize the CSS selectors based on the real website
        for row in soup.select(".load-row"):
            title = row.select_one(".load-title").get_text(strip=True)
            origin = row.select_one(".load-origin").get_text(strip=True)
            destination = row.select_one(".load-destination").get_text(strip=True)
            url = row.select_one("a.load-details")["href"]

            # Normalize relative URLs into absolute URLs
            if not url.startswith("http"):
                url = self.BASE_URL.rstrip("/") + "/" + url.lstrip("/")

            leads.append(
                OpenWebLeadCreate(
                    source=self.source_name,
                    title=title,
                    origin=origin,
                    destination=destination,
                    raw_url=url,
                    posted_at=datetime.utcnow(),
                )
            )

        return leads
