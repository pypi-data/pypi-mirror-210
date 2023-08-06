from Twitch.API.Resources.__imports import *

class CreateEventSubSubscriptionRequest(Utils.RequestBaseClass):
        requestType = Utils.HTTPMethod.POST
        scope = Scope.Channel.Manage.Redemptions
        authorization = Utils.AuthRequired.USER
        endPoint ="//channel_points//custom_rewards"
    

class CreateEventSubSubscriptionResponse(Utils.ResponseBaseClass):
        def __init__(self) -> None:
            super().__init__()

class DeleteEventSubSubscriptionRequest(Utils.RequestBaseClass):
        requestType = Utils.HTTPMethod.POST
        scope = Scope.Channel.Manage.Redemptions
        authorization = Utils.AuthRequired.USER
        endPoint ="//channel_points//custom_rewards"
    

class DeleteEventSubSubscriptionResponse(Utils.ResponseBaseClass):
        def __init__(self) -> None:
            super().__init__()

class GetEventSubSubscriptionsRequest(Utils.RequestBaseClass):
        requestType = Utils.HTTPMethod.POST
        scope = Scope.Channel.Manage.Redemptions
        authorization = Utils.AuthRequired.USER
        endPoint ="//channel_points//custom_rewards"
    

class GetEventSubSubscriptionsResponse(Utils.ResponseBaseClass):
        def __init__(self) -> None:
            super().__init__()