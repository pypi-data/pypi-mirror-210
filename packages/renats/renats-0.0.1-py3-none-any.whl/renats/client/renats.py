import asyncio
from typing import Any

import msgpack
import nats
from msgpack import OutOfData
from nats.aio.client import Client
from nats.errors import NoRespondersError

from renats import loggers
from renats.dispatcher.dispatcher import Dispatcher
from renats.exceptions import NatsClientError, InvalidPayloadData, NoResponders


class ReNats:
    def __init__(self, servers: list[str]):
        self.servers: list[str] = servers
        self.nats_client: Client | None = None

    async def request(
            self,
            service: str,
            method: str,
            data: dict[str, Any],
            *,
            headers: dict[str, str] | None = None,
            timeout: float = 0.5
    ) -> dict[str, Any]:
        if not self.nats_client:
            loggers.renats.info("Connecting to NATS servers")
            self.nats_client = await nats.connect(self.servers)
        if self.nats_client.is_closed:
            raise NatsClientError("NATS client closed")

        subject = f"{service}.{method}"

        if not isinstance(data, dict):
            raise InvalidPayloadData("Request data must be a dictionary object", data)

        try:
            payload = msgpack.packb(data)
        except (OutOfData, ValueError):
            raise InvalidPayloadData("Error where packing request data", data)

        try:
            response = await self.nats_client.request(
                subject=subject,
                payload=payload,
                timeout=timeout,
                headers=headers if headers else {}
            )

            try:
                data = msgpack.unpackb(response.data)
            except ValueError:
                raise InvalidPayloadData("Error where unpacking response data (bytes)", response.data)
            if not isinstance(data, dict):
                raise InvalidPayloadData("Response data must be a dictionary object", response.data)

            return data
        except NoRespondersError:
            raise NoResponders(f"No responders available for request in subject {subject}")

    async def polling(self, dispatcher: Dispatcher):
        if not self.nats_client:
            loggers.renats.info("Connecting to NATS servers")
            self.nats_client = await nats.connect(self.servers)
        loggers.renats.info(f"Run polling for {dispatcher.base_subject}")
        subscription = await self.nats_client.subscribe(f"{dispatcher.base_subject}.*")
        async for message in subscription.messages:
            asyncio.create_task(dispatcher.feed_message(message))
