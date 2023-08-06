from http import HTTPMethod
from typing import Optional
import asyncio, aiohttp
from aiohttp import ClientResponse

class APIRequest():
    def __init__(self, apiURL:str) -> None:
        self._seesion = aiohttp.ClientSession() 
        self._apiURL = apiURL
        self._RequestFunc: dict = {
            HTTPMethod.DELETE : self._seesion.delete,
            HTTPMethod.GET : self._seesion.get,
            HTTPMethod.PATCH : self._seesion.patch,
            HTTPMethod.POST : self._seesion.post,
            HTTPMethod.PUT : self._seesion.put,
        }

    async def request(self, endPoint:str, method:HTTPMethod, headers:Optional[dict[str,str]]=None, params=None)-> ClientResponse:
                response = await self._RequestFunc[method](f"{self._apiURL + endPoint}", headers=headers, params=params)
                await asyncio.sleep(0)
                return response
    
    async def close(self):
           await asyncio.sleep(0)
           await self._seesion.close()