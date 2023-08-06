from Twitch.API.Resources.__imports import *

class SendWhisperRequest(Utils.RequestBaseClass):
    requestType = Utils.HTTPMethod.POST
    scope = Scope.User.Manage.Whispers
    authorization = Utils.AuthRequired.USER
    endPoint ="/whispers"
    def __init__(self, from_user_id: str, to_user_id: str, message: str) -> None:
            self.from_user_id: str = from_user_id
            self.to_user_id: str = to_user_id
            self.message: str = message
            super().__init__()
    
class SendWhisperResponse(Utils.ResponseBaseClass):
    def __init__(self) -> None:
        super().__init__(None)