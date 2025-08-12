import asyncio
import logging
from typing import Awaitable, Any

_background_tasks: set[asyncio.Task[Any]] = set()


def schedule(coro: Awaitable[Any], description: str) -> asyncio.Task[Any]:
    """Schedule a coroutine to run in background and log its status."""
    async def runner() -> Any:
        logging.info("Starting background task: %s", description)
        try:
            result = await coro
            logging.info("Background task completed: %s", description)
            return result
        except Exception as e:  # pragma: no cover - logging
            logging.exception("Background task failed (%s): %s", description, e)
            raise

    task = asyncio.create_task(runner())
    _background_tasks.add(task)
    task.add_done_callback(_background_tasks.discard)
    return task
