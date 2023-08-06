from Twitch.API.Resources.__imports import *

class GetBroadcasterSubscriptionsRequest(Utils.RequestBaseClass):
        requestType = Utils.HTTPMethod.POST
        scope = Scope.Channel.Manage.Redemptions
        authorization = Utils.AuthRequired.USER
        endPoint ="//channel_points//custom_rewards"
    

class GetBroadcasterSubscriptionsResponse(Utils.ResponseBaseClass):
        def __init__(self) -> None:
            super().__init__()

class CheckUserSubscriptionRequest(Utils.RequestBaseClass):
        requestType = Utils.HTTPMethod.POST
        scope = Scope.Channel.Manage.Redemptions
        authorization = Utils.AuthRequired.USER
        endPoint ="//channel_points//custom_rewards"
    

class CheckUserSubscriptionResponse(Utils.ResponseBaseClass):
        def __init__(self) -> None:
            super().__init__()
