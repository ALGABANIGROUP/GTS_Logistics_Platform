from __future__ import annotations

from typing import Any, Dict

from backend.ai.learning_bot_base import ReusableLearningBot


class FinanceBotLearningBot(ReusableLearningBot):
    name = "finance_bot"
    description = "Financial analysis with learning"
    learning_frequency = "daily"
    learning_intensity = "high"

    async def process_invoice(self, invoice_data: Dict[str, Any]) -> Dict[str, Any]:
        return await self.process_action("process_invoice", invoice=invoice_data)

    async def _execute_action(self, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        invoice = params.get("invoice", {})
        amount = float(invoice.get("amount") or 0)
        return {
            "status": "approved" if amount <= 10000 else "manual_review",
            "amount": amount,
            "currency": invoice.get("currency") or "CAD",
            "accuracy": 0.96,
        }


finance_bot = FinanceBotLearningBot()

