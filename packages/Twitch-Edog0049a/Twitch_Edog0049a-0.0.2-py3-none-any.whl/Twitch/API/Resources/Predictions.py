from Twitch.API.Resources.__imports import *

class GetPredictionsRequest(Utils.RequestBaseClass):
        requestType = Utils.HTTPMethod.POST
        scope = Scope.Channel.Manage.Redemptions
        authorization = Utils.AuthRequired.USER
        endPoint ="//channel_points//custom_rewards"
    

class GetPredictionsResponse(Utils.ResponseBaseClass):
        def __init__(self) -> None:
            super().__init__()

class CreatePredictionRequest(Utils.RequestBaseClass):
        requestType = Utils.HTTPMethod.POST
        scope = Scope.Channel.Manage.Redemptions
        authorization = Utils.AuthRequired.USER
        endPoint ="//channel_points//custom_rewards"
    

class CreatePredictionResponse(Utils.ResponseBaseClass):
        def __init__(self) -> None:
            super().__init__()

class EndPredictionRequest(Utils.RequestBaseClass):
        requestType = Utils.HTTPMethod.POST
        scope = Scope.Channel.Manage.Redemptions
        authorization = Utils.AuthRequired.USER
        endPoint ="//channel_points//custom_rewards"
    

class EndPredictionResponse(Utils.ResponseBaseClass):
        def __init__(self) -> None:
            super().__init__()