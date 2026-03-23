from typing import Dict, Protocol, Any

class AIBot(Protocol):
    name: str
    async def run(self, payload: dict) -> dict: ...
    async def status(self) -> dict: ...
    async def config(self) -> dict: ...

class AIRegistry:
    def __init__(self) -> None:
        self._bots: Dict[str, AIBot] = {}

    def register(self, bot: AIBot) -> None:
        self._bots[bot.name] = bot

    def get(self, name: str) -> AIBot:
        return self._bots[name]

    def list(self) -> Dict[str, str]:
        return {k: v.__class__.__name__ for k, v in self._bots.items()}

registry = AIRegistry()
