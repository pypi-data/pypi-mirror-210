from typing import Final

import msgpack
import nats
from nats.aio.client import Client

from renats.exceptions import InvalidDataFormat, RequestMethodError

DEFAULT_TIMEOUT: Final[float] = 0.5


class RenatsClient:
    def __init__(
            self,
            name: str,
            *,
            timeout: float = DEFAULT_TIMEOUT,
            headers: dict[str, str] = None
    ):
        self.name: str = name
        self.timeout: float = timeout
        self.headers: dict[str, str] = {} if headers is None else headers
        self.nats_client: Client | None = None

    async def connect(self, servers: list[str]):
        self.nats_client = await nats.connect(servers)

    async def request(self, method: str, headers: dict[str, str] = None, **params) -> tuple[int, str]:
        request_headers = self.headers.copy()
        if headers is not None:
            request_headers.update(headers)

        packed_params = msgpack.packb(params)

        response_message = await self.nats_client.request(
            f"{self.name}.{method}",
            packed_params,
            timeout=self.timeout,
            headers=request_headers
        )

        response = msgpack.unpackb(response_message.data)

        if not isinstance(response, dict):
            raise InvalidDataFormat("Invalid response format: data must be a dictionary object", response)
        status = response.get("status")
        if status is None:
            raise InvalidDataFormat("Invalid response format: missing status", response)
        if not isinstance(status, int):
            raise InvalidDataFormat("Invalid response format: status must be an integer object", response)

        error = response.get("error")
        if error is not None:
            raise RequestMethodError(response["status"], response["error"])

        return status, response.get("data")


