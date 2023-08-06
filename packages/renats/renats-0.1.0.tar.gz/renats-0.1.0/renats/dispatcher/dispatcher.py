import asyncio
from typing import Any

import msgpack
from nats.aio.msg import Msg

from renats import loggers
from renats.dispatcher.router import Router
from renats.exceptions import InvalidDataFormat, RequestMethodError


class Dispatcher(Router):
    def __init__(self, name: str, **kwargs):
        super().__init__()
        self.name: str = name
        self.dependencies: dict[str, Any] = kwargs

    async def feed_message(self, message: Msg):
        loop = asyncio.get_running_loop()

        method = message.subject[len(self.name) + 1:]
        callback = self.route(method)

        if not callback:
            loggers.dispatcher.info(f"Request from '{method}' is not handled")
            return

        params = msgpack.unpackb(message.data)

        if not isinstance(params, dict):
            raise InvalidDataFormat(f"Request data from '{method}' must be a dictionary object", params)

        start_time = loop.time()

        try:
            response_status, response_data = await callback(
                headers=message.headers,
                **params,
                **self.dependencies
            )
            response = {
                "status": response_status,
                "data": response_data
            }
        except RequestMethodError as exception:
            response = {
                "status": exception.status,
                "error": exception.error
            }

        await message.respond(msgpack.packb(response))

        finish_time = loop.time()
        duration = (finish_time - start_time) * 1000
        loggers.dispatcher.info(f"Request from '{method}' is handled. Duration {duration:.4f} ms")


