# moved from backend/email/bos_integration.py

"""
BotOS Integration for Email System
"""
from typing import Any, Dict, List


class EmailBotIntegration:
	"""Integrates email processing with Bot Operating System"""
    
	def __init__(self):
		self.email_to_bot_mapping = {
			"support@gabanilogistics.com": {
				"bot": "customer_service",
				"workflows": ["customer_inquiry", "support_ticket"],
				"auto_execute": True
			},
			"accounts@gabanilogistics.com": {
				"bot": "finance_bot",
				"workflows": ["invoice_processing", "payment_confirmation"],
				"auto_execute": True
			}
		}
		self.execution_history: List[Dict[str, Any]] = []
    
	async def route_email_to_bot(self, email: Dict[str, Any]) -> Dict[str, Any]:
		"""Route email to appropriate bot for processing"""
		to_address = email.get("to", "").lower()
        
		config = self.email_to_bot_mapping.get(to_address)
		if not config:
			config = {"bot": "general_manager", "workflows": ["general_inquiry"], "auto_execute": False}
        
		result = {
			"bot": config["bot"],
			"workflow": config["workflows"][0] if config["workflows"] else "default",
			"executed": config["auto_execute"],
			"priority": "medium"
		}
        
		# Track execution
		self.execution_history.append({
			"email_id": email.get("id"),
			"bot": result["bot"],
			"workflow": result["workflow"],
			"status": "executed" if result["executed"] else "pending",
			"timestamp": None
		})
        
		return result
    
	def get_bot_for_email(self, email_account: str) -> str:
		"""Get the bot assigned to handle an email account"""
		config = self.email_to_bot_mapping.get(email_account.lower())
		return config["bot"] if config else "general_manager"
    
	def get_execution_history(self, limit: int = 50) -> List[Dict[str, Any]]:
		"""Get recent email-to-bot execution history"""
		return self.execution_history[-limit:]
