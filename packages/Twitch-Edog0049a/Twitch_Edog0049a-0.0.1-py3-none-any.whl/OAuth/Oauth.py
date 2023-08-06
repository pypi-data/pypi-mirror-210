from typing import Any, Optional
import aiohttp
4
from http import HTTPMethod
class TokenResponse:
    def __init__(self, responseData: dict) -> None:
        self.access_token:str = responseData.get("access_token")
        self.refresh_token: str =  responseData.get("refresh_token")
        self.scope: list = responseData.get("scope")
        self.token_type:str = responseData.get("token_type")
class twitchOauth():
    OAUTH_URL = "https://id.twitch.tv/oauth2/"

    def __init__(self, client_id: str, client_secret: str, scopes: list, redirectUrl:Optional[str]=None) -> None:
        self.onRequestData = lambda data: data
        self._client_id: str = client_id
        self._client_secret: str = client_secret
        self._scope: str  =  "+".join([str(scope) for scope in scopes]) 
        self._redirectURL = redirectUrl if redirectUrl else "http://localhost"
        self._csrf = ""
        print(self._scope)

    def getCodeURL(self, CSRF)->str:
        
        self._csrf = CSRF
        return f"{self.OAUTH_URL}authorize?response_type=code&client_id={self._client_id}&redirect_uri={self._redirectURL}&scope={self._scope}&state={CSRF}"
    
    @staticmethod
    async def _oauthRequest(url: str, Method:HTTPMethod , data:Optional[dict[str, Any]] = None, headers:Optional[dict[str,Any]] = None) -> aiohttp.client.ClientResponse.json:
        session = aiohttp.ClientSession()
        response: aiohttp.client.ClientResponse = None
        if Method == HTTPMethod.POST:
            response: aiohttp.client.ClientResponse = await session.post(url=url,data=data, headers=headers)
        if HTTPMethod == HTTPMethod.GET:
            response: aiohttp.client.ClientResponse = await session.get(url=url, data=data, headers=headers)
        async with response:
            data = await response.json()
            if response.status == 200:
                await session.close() 
                return data
            await session.close()
            raise twitchOauth._handleResponseError(data)
    
    async def GetClientToken(self) -> TokenResponse:
        url = f"{self.OAUTH_URL}token"
        data = {
            'client_id' : self._client_id,
            'client_secret' : self._client_secret,
            'grant_type' : 'client_credentials'
        }
        responseDict = await self._oauthRequest(url, HTTPMethod.POST, data=data)
        return TokenResponse(responseDict)
    
    async def refreshToken(self, refreshToken: str) -> TokenResponse:
        url = f"{self.OAUTH_URL}token"
        data = {
            'client_id' : self._client_id,
            'client_secret' : self._client_secret,
            'grant_type' : 'refresh_token',  
            'refresh_token' : refreshToken
        }
        responseDict = await self._oauthRequest(url, HTTPMethod.POST, data=data)
        return TokenResponse(responseDict)


    async def getTokenFromCode(self, code:str) -> TokenResponse:
        url = f"{self.OAUTH_URL}token"
        data = {
            'client_id' : self._client_id,
            'client_secret' : self._client_secret,
            'code' : code,
            'grant_type' : 'authorization_code',
            'redirect_uri' : self._redirectURL                               
        }
        responseDict = await self._oauthRequest(url, HTTPMethod.POST, data=data)
        if responseDict.get("error"):
            raise self._handleResponseError(responseDict)
        return TokenResponse(responseDict)
    
    @staticmethod
    async def vaidateToken(token) -> tuple[bool,str]:
        url = f"{twitchOauth.OAUTH_URL}validate"
        headers = {
            'Authorization': f'OAuth {token}'
        }
        try:
            return (True, await twitchOauth._oauthRequest(url, HTTPMethod.GET, headers=headers))
        except Exception as e:
            print(e)
            return (False, e)
            
    def _handleResponseError(responseData: dict) -> None:
        raise Exception(responseData)