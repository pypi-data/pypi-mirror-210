import asyncio
from typing import Any

import msgpack
from msgpack import OutOfData
from nats.aio.msg import Msg

from renats import loggers
from renats.dispatcher.router import Router
from renats.exceptions import InvalidPayloadData


class Dispatcher(Router):
    def __init__(self, base_subject: str, **kwargs):
        super().__init__()
        self.base_subject: str = base_subject
        self.dependencies: dict[str, Any] = kwargs

    async def feed_message(self, message: Msg):
        loop = asyncio.get_running_loop()

        request_subject = message.subject[len(self.base_subject) + 1:]
        loggers.dispatcher.info(f"Received request from '{request_subject}' ('{message.subject}')")
        callback = self.route(request_subject)

        if not callback:
            loggers.dispatcher.info(f"Request from '{request_subject}' is not handled")
            return

        try:
            data = msgpack.unpackb(message.data)
        except ValueError:
            raise InvalidPayloadData(f"Error while unpacking request data from '{request_subject}'", message.data)

        if not isinstance(data, dict):
            raise InvalidPayloadData(f"Request data from '{request_subject}' must be a dictionary object", data)

        start_time = loop.time()
        raw_response = await callback(
            headers=message.headers,
            data=data,
            **self.dependencies
        )

        if not isinstance(raw_response, dict):
            raise InvalidPayloadData("Response data must be a dictionary object", raw_response)

        try:
            payload = msgpack.packb(raw_response)
        except (OutOfData, ValueError):
            raise InvalidPayloadData("Error where packing response data", data)

        await message.respond(payload)

        finish_time = loop.time()
        duration = (finish_time - start_time) * 1000
        loggers.dispatcher.info(f"Request from '{request_subject}' is handled. Duration {round(duration, 4)} ms")


