"""Temporal worker — registers the 'leads' task queue."""

import asyncio
import logging
import os

from temporalio.client import Client
from temporalio.worker import Worker

TASK_QUEUE = "leads"

logger = logging.getLogger(__name__)


async def main() -> None:
    address = os.getenv("TEMPORAL_ADDRESS", "localhost:7233")
    client = await Client.connect(address)
    logger.info("connected to temporal")
    # workflows and activities wired in once DSPy/LangGraph modules exist
    async with Worker(client, task_queue=TASK_QUEUE, workflows=[], activities=[]):
        await asyncio.Event().wait()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
