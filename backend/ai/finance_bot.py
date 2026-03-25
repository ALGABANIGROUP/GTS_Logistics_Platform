from __future__ import annotations

from typing import Any, Dict

from backend.ai.learning_bot_base import ReusableLearningBot
from backend.services.auto_reply_service import get_auto_reply


class FinanceBotLearningBot(ReusableLearningBot):
    name = "finance_bot"
    description = "Financial analysis with learning"
    learning_frequency = "daily"
    learning_intensity = "high"

    async def process_invoice(self, invoice_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process invoice and send auto-reply"""
        try:
            # Process invoice logic here
            result = await self._process_invoice_internal(invoice_data)
            
            # Send auto-reply if enabled
            auto_reply = get_auto_reply()
            if auto_reply.enabled and invoice_data.get('email'):
                auto_reply.send_auto_reply(
                    to_email=invoice_data['email'],
                    name=invoice_data.get('name', 'Customer'),
                    inquiry_type='billing',
                    reference=result.get('invoice_id')
                )
            
            return result
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _process_invoice_internal(self, invoice_data: Dict[str, Any]) -> Dict[str, Any]:
        """Internal invoice processing logic"""
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

