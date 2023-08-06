import asyncio

import nats
from nats.aio.client import Client

from renats import loggers
from renats.dispatcher.dispatcher import Dispatcher


class Renats:
    def __init__(self, dispatcher: Dispatcher):
        self.dispatcher: Dispatcher = dispatcher
        self.nats_client: Client | None = None

    async def polling(self, servers: list[str]):
        if not self.nats_client:
            loggers.renats.info("Connecting to NATS servers")
            self.nats_client = await nats.connect(servers)
        loggers.renats.info(f"Run polling for {self.dispatcher.name}")
        subscription = await self.nats_client.subscribe(f"{self.dispatcher.name}.*")
        async for message in subscription.messages:
            asyncio.create_task(self.dispatcher.feed_message(message))
