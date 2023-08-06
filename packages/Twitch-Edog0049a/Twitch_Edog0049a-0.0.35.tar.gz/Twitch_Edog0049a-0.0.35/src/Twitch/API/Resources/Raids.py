from Twitch.API.Resources.__imports import *

class StartaraidRequest(Utils.RequestBaseClass):
        requestType = Utils.HTTPMethod.POST
        scope = Scope.Channel.Manage.Redemptions
        authorization = Utils.AuthRequired.USER
        endPoint ="//channel_points//custom_rewards"
    

class StartaraidResponse(Utils.ResponseBaseClass):
        def __init__(self) -> None:
            super().__init__()

class CancelaraidRequest(Utils.RequestBaseClass):
        requestType = Utils.HTTPMethod.POST
        scope = Scope.Channel.Manage.Redemptions
        authorization = Utils.AuthRequired.USER
        endPoint ="//channel_points//custom_rewards"
    

class CancelaraidResponse(Utils.ResponseBaseClass):
        def __init__(self) -> None:
            super().__init__()
