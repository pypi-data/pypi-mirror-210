from collections import defaultdict
import asyncio
import logging

logger = logging.getLogger(__name__)


class QueueBovinePubSub:
    def __init__(self):
        self.queues = defaultdict(asyncio.Queue)

    async def send(self, endpoint_path, data):
        await self.queues[endpoint_path].put(data)

    async def event_stream(self, endpoint_path):
        while True:
            data = await self.queues[endpoint_path].get()
            yield data
            yield "\n".encode("utf-8")
