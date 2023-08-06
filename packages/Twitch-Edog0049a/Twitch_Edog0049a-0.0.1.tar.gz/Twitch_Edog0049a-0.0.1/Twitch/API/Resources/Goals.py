from Twitch.API.Resources.__imports import *
class GetCreatorGoalsRequest(Utils.RequestBaseClass):
        requestType = Utils.HTTPMethod.POST
        scope = Scope.Channel.Manage.Redemptions
        authorization = Utils.AuthRequired.USER
        endPoint ="//channel_points//custom_rewards"
    

class GetCreatorGoalsResponse(Utils.ResponseBaseClass):
        def __init__(self) -> None:
            super().__init__()
