from typing import Any, Callable, Awaitable

CallbackType = Callable[..., Awaitable[dict[str, Any]]]


class Router:
    def __init__(self):
        self._callbacks: dict[str, CallbackType] = {}

    def include_router(self, router: "Router"):
        self._callbacks.update(router._callbacks)

    def include_routers(self, *routers: "Router"):
        for router in routers:
            self.include_router(router)

    def route(self, subject: str) -> CallbackType | None:
        return self._callbacks.get(subject)

    def register_callback(self, method: str, callback: CallbackType):
        self._callbacks[method] = callback

    def callback(self, method: str):
        def wrapper(callback: CallbackType):
            self.register_callback(
                method=method,
                callback=callback
            )
            return callback
        return wrapper

