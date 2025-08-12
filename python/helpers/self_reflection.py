from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Dict

from python.helpers.memory import Memory


class SelfReflection:

    def __init__(self, agent, interval: int = 3600) -> None:
        self.agent = agent
        self.interval = interval
        self._task: asyncio.Task | None = None

    async def start(self) -> None:
        if self._task is None:
            self._task = asyncio.create_task(self._run())

    async def _run(self) -> None:
        while True:
            await asyncio.sleep(self.interval)
            await SelfReflection.analyze(self.agent)

    @staticmethod
    async def analyze(agent, log_dir: str = "logs") -> Dict[str, int]:
        base = Path(log_dir)
        metrics = {"total_lines": 0, "error_lines": 0}
        for file in base.glob("*.log"):
            try:
                with file.open() as f:
                    for line in f:
                        metrics["total_lines"] += 1
                        if "error" in line.lower():
                            metrics["error_lines"] += 1
            except FileNotFoundError:
                continue
        db = await Memory.get(agent)
        await db.insert_text(str(metrics), {"area": Memory.Area.MAIN.value, "tag": "self_reflection"})
        return metrics
