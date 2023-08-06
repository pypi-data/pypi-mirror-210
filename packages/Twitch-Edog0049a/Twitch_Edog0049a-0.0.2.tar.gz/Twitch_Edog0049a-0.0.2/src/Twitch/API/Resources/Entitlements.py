from Twitch.API.Resources.__imports import *
class GetDropsEntitlementsRequest(Utils.RequestBaseClass):
        requestType = Utils.HTTPMethod.POST
        scope = Scope.Channel.Manage.Redemptions
        authorization = Utils.AuthRequired.USER
        endPoint ="//channel_points//custom_rewards"
    

class GetDropsEntitlementsResponse(Utils.ResponseBaseClass):
        def __init__(self) -> None:
            super().__init__()

class UpdateDropsEntitlementsRequest(Utils.RequestBaseClass):
        requestType = Utils.HTTPMethod.POST
        scope = Scope.Channel.Manage.Redemptions
        authorization = Utils.AuthRequired.USER
        endPoint ="//channel_points//custom_rewards"
    

class UpdateDropsEntitlementsResponse(Utils.ResponseBaseClass):
        def __init__(self) -> None:
            super().__init__()