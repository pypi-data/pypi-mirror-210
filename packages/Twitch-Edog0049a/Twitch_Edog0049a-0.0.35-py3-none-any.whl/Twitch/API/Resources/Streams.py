from Twitch.API.Resources.__imports import *

class GetStreamKeyRequest(Utils.RequestBaseClass):
        requestType = Utils.HTTPMethod.POST
        scope = Scope.Channel.Manage.Redemptions
        authorization = Utils.AuthRequired.USER
        endPoint ="//channel_points//custom_rewards"
    

class GetStreamKeyResponse(Utils.ResponseBaseClass):
        def __init__(self) -> None:
            super().__init__()

class GetStreamsRequest(Utils.RequestBaseClass):
        requestType = Utils.HTTPMethod.POST
        scope = Scope.Channel.Manage.Redemptions
        authorization = Utils.AuthRequired.USER
        endPoint ="//channel_points//custom_rewards"
    

class GetStreamsResponse(Utils.ResponseBaseClass):
        def __init__(self) -> None:
            super().__init__()

class GetFollowedStreamsRequest(Utils.RequestBaseClass):
        requestType = Utils.HTTPMethod.POST
        scope = Scope.Channel.Manage.Redemptions
        authorization = Utils.AuthRequired.USER
        endPoint ="//channel_points//custom_rewards"
    

class GetFollowedStreamsResponse(Utils.ResponseBaseClass):
        def __init__(self) -> None:
            super().__init__()

class CreateStreamMarkerRequest(Utils.RequestBaseClass):
        requestType = Utils.HTTPMethod.POST
        scope = Scope.Channel.Manage.Redemptions
        authorization = Utils.AuthRequired.USER
        endPoint ="//channel_points//custom_rewards"
    

class CreateStreamMarkerResponse(Utils.ResponseBaseClass):
        def __init__(self) -> None:
            super().__init__()

class GetStreamMarkersRequest(Utils.RequestBaseClass):
        requestType = Utils.HTTPMethod.POST
        scope = Scope.Channel.Manage.Redemptions
        authorization = Utils.AuthRequired.USER
        endPoint ="//channel_points//custom_rewards"
    

class GetStreamMarkersResponse(Utils.ResponseBaseClass):
        def __init__(self) -> None:
            super().__init__()
