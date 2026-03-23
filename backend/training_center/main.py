from __future__ import annotations

import asyncio
import json
import tempfile
from pathlib import Path

from .trainer_bot import TrainerBot


async def run_demo() -> dict[str, object]:
    with tempfile.TemporaryDirectory(prefix="training-center-demo-") as temp_dir:
        trainer = TrainerBot(reports_dir=Path(temp_dir), seed=7)
        bots = trainer.list_trainable_bots()
        await trainer.register_bot("security_manager_bot", level="intermediate", version="2.0")
        assessment = await trainer.assess_bot_capabilities("security_manager_bot")
        plan = await trainer.create_training_plan("security_manager_bot")
        result = await trainer.start_training_session(plan["plan_id"])
        stats = trainer.get_stats()
        return {"bots": bots, "assessment": assessment, "plan": plan, "result": result, "stats": stats}


def main() -> None:
    payload = asyncio.run(run_demo())
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
