from __future__ import annotations

from datetime import date

from fastapi import APIRouter
from fastapi.responses import PlainTextResponse, Response

router = APIRouter(tags=["seo"])

SITE_URL = "https://www.gtsdispatcher.com"

SITEMAP_PAGES = [
    {"url": "/", "priority": "1.0", "changefreq": "weekly"},
    {"url": "/about", "priority": "0.7", "changefreq": "monthly"},
    {"url": "/resources", "priority": "0.8", "changefreq": "weekly"},
    {"url": "/pricing", "priority": "0.8", "changefreq": "monthly"},
    {"url": "/products", "priority": "0.8", "changefreq": "monthly"},
    {"url": "/contact", "priority": "0.8", "changefreq": "monthly"},
    {"url": "/blog", "priority": "0.8", "changefreq": "weekly"},
    {"url": "/partners", "priority": "0.6", "changefreq": "monthly"},
    {"url": "/find-loads", "priority": "0.7", "changefreq": "weekly"},
    {"url": "/fraud-prevention", "priority": "0.6", "changefreq": "monthly"},
    {"url": "/privacy", "priority": "0.3", "changefreq": "yearly"},
    {"url": "/terms", "priority": "0.3", "changefreq": "yearly"},
    {"url": "/legal", "priority": "0.3", "changefreq": "yearly"},
]


@router.get("/robots.txt", response_class=PlainTextResponse, include_in_schema=False)
async def robots_txt() -> str:
    return "\n".join(
        [
            "User-agent: *",
            "Allow: /",
            "Disallow: /admin/",
            "Disallow: /_debug/",
            "Disallow: /api/v1/",
            "Disallow: /test/",
            "Disallow: /health/",
            "Disallow: /docs",
            "Disallow: /openapi.json",
            "",
            f"Sitemap: {SITE_URL}/sitemap.xml",
            "",
        ]
    )


@router.get("/sitemap.xml", response_class=Response, include_in_schema=False)
async def sitemap_xml() -> Response:
    today = date.today().isoformat()
    lines = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']

    for page in SITEMAP_PAGES:
        lines.extend(
            [
                "  <url>",
                f"    <loc>{SITE_URL}{page['url']}</loc>",
                f"    <lastmod>{today}</lastmod>",
                f"    <changefreq>{page['changefreq']}</changefreq>",
                f"    <priority>{page['priority']}</priority>",
                "  </url>",
            ]
        )

    lines.append("</urlset>")
    return Response(content="\n".join(lines), media_type="application/xml")
