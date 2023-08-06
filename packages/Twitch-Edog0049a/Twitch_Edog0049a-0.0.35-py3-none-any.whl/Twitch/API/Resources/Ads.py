from Twitch.API.Resources.__imports import *

"""
Start Commercial
"""

class StartCommercialRequest(Utils.RequestBaseClass):
    requestType = Utils.HTTPMethod.POST
    scope = Scope.Channel.Edit.Commercial
    authorization = Utils.AuthRequired.USER
    endPoint = "/channels/commercial"
    def __init__(self, broadcaster_id: str, length: int ) -> None:
        self.broadcaster_id: str = broadcaster_id
        self.length:int = length
        super().__init__()

class StartCommercialItem:
    length: int 
    message: str
    retry_after: int 

class StartCommercialRepsonse(Utils.ResponseBaseClass):
    def __init__(self) -> None:
        super().__init__(StartCommercialItem)
    