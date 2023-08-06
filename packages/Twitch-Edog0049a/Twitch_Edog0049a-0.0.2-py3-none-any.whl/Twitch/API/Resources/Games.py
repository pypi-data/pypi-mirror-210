from Twitch.API.Resources.__imports import *

class GetTopGamesRequest(Utils.RequestBaseClass):
        requestType = Utils.HTTPMethod.POST
        scope = Scope.Channel.Manage.Redemptions
        authorization = Utils.AuthRequired.USER
        endPoint ="//channel_points//custom_rewards"
    

class GetTopGamesResponse(Utils.ResponseBaseClass):
        def __init__(self) -> None:
            super().__init__()

class GetGamesRequest(Utils.RequestBaseClass):
        requestType = Utils.HTTPMethod.POST
        scope = Scope.Channel.Manage.Redemptions
        authorization = Utils.AuthRequired.USER
        endPoint ="//channel_points//custom_rewards"
    

class GetGamesResponse(Utils.ResponseBaseClass):
        def __init__(self) -> None:
            super().__init__()