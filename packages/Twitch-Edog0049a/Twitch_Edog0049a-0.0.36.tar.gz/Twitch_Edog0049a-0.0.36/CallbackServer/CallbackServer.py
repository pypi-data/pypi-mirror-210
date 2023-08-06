import asyncio
import ssl
from aiohttp import  web
from typing import Callable, Optional, Awaitable
import certifi
from enum import Enum

class Method(Enum):
    POST = "POST"
    GET = "GET"
    DELETE ="DELETE"
class CallbackHandler:
    METHODS: Method = Method
    def __init__(self, path: str, method:Method , func: Awaitable) -> None:
        self.path = path
        self.method: Method = method
        self.func: Awaitable = func

class CallbackServer():
    def __init__(self, callbacks:list[CallbackHandler], host:Optional[str]=None, port:Optional[int]=None) -> None:
        """
        callbacks dict[method as string, callback function]
        """
        self._webserver:web.Application = web.Application()
        self._routes: list = []
        self._host: str = host if host else "localhost"
        self._port: int = port if port else 8880
        self._run: bool = True
        self._runner = web.AppRunner(self._webserver)
        self._server: web.TCPSite
        for callback in callbacks:
            self._webserver.router.add_route(method=callback.method.value, path=callback.path, handler=callback.func)

    async def start(self) -> None:
        context = context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_verify_locations(certifi.where())
        await self._runner.setup()
        self._server = web.TCPSite(runner=self._runner, host=self._host, port=self._port)
        await self._server.start()
        while self._run:
            await asyncio.sleep(0)
           
   
    async def stop(self):
        await self._server.stop()
        self._run = False