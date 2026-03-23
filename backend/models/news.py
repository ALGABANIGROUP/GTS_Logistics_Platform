from __future__ import annotations

from dataclasses import dataclass
from typing import List
from backend.models.monthly_report import MonthlyReport  # type: ignore[import]


@dataclass
class MonthlyNewsItem:
    """
    Simple DTO for monthly financial news.
    """
    title: str
    summary: str


def build_news_for_report(report: MonthlyReport) -> MonthlyNewsItem:
    """
    Build a human-readable news item from a single MonthlyReport row.
    Uses fields defined in backend.models.monthly_report:
      - period
      - total_revenue
      - total_expenses
      - net_profit
    """

    period = getattr(report, "period", None) or "Unknown period"
    total_revenue = float(getattr(report, "total_revenue", 0.0) or 0.0)
    total_expenses = float(getattr(report, "total_expenses", 0.0) or 0.0)
    net_profit = float(
        getattr(report, "net_profit", total_revenue - total_expenses) or 0.0
    )

    title = f"GTS Logistics Monthly Performance – {period}"

    summary = (
        f"For {period}, total revenue was ${total_revenue:,.2f}, "
        f"total expenses were ${total_expenses:,.2f}, "
        f"resulting in net profit of ${net_profit:,.2f}."
    )

    if net_profit < 0:
        summary += " The company recorded a net loss this period; review major expense drivers."
    elif net_profit < (0.1 * total_revenue if total_revenue > 0 else 0):
        summary += " Profit margin is relatively low; consider optimizing operating costs."
    else:
        summary += " Overall performance is healthy with a positive profit margin."

    return MonthlyNewsItem(title=title, summary=summary)


def build_news_for_reports(reports: List[MonthlyReport]) -> List[MonthlyNewsItem]:
    """
    Build news items for a list of MonthlyReport rows.
    """
    return [build_news_for_report(r) for r in reports]

