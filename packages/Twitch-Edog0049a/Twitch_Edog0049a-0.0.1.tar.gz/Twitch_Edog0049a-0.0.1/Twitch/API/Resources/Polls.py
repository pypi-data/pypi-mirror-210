from Twitch.API.Resources.__imports import *

class GetPollsRequest(Utils.RequestBaseClass):
        requestType = Utils.HTTPMethod.POST
        scope = Scope.Channel.Manage.Redemptions
        authorization = Utils.AuthRequired.USER
        endPoint ="//channel_points//custom_rewards"
    

class GetPollsResponse(Utils.ResponseBaseClass):
        def __init__(self) -> None:
            super().__init__()

class CreatePollRequest(Utils.RequestBaseClass):
        requestType = Utils.HTTPMethod.POST
        scope = Scope.Channel.Manage.Redemptions
        authorization = Utils.AuthRequired.USER
        endPoint ="//channel_points//custom_rewards"
    

class CreatePollResponse(Utils.ResponseBaseClass):
        def __init__(self) -> None:
            super().__init__()

class EndPollRequest(Utils.RequestBaseClass):
        requestType = Utils.HTTPMethod.POST
        scope = Scope.Channel.Manage.Redemptions
        authorization = Utils.AuthRequired.USER
        endPoint ="//channel_points//custom_rewards"
    

class EndPollResponse(Utils.ResponseBaseClass):
        def __init__(self) -> None:
            super().__init__()