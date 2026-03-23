class MapleLoadBot:
    name = "mapleload"
    display_name = "MapleLoad AI"

    async def run(self, payload: dict) -> dict:
        # Minimal safe stub to prove wiring works.
        # Replace this with real MapleLoad logic later.
        return {
            "ok": True,
            "bot": "mapleload",
            "received": payload,
            "note": "MapleLoadBot loaded successfully (stub)."
        }
