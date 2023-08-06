from Twitch.API.Resources.__imports import *

class GetChannelStreamScheduleRequest(Utils.RequestBaseClass):
        requestType = Utils.HTTPMethod.POST
        scope = Scope.Channel.Manage.Redemptions
        authorization = Utils.AuthRequired.USER
        endPoint ="//channel_points//custom_rewards"
    

class GetChannelStreamScheduleResponse(Utils.ResponseBaseClass):
        def __init__(self) -> None:
            super().__init__()

class GetChanneliCalendarRequest(Utils.RequestBaseClass):
        requestType = Utils.HTTPMethod.POST
        scope = Scope.Channel.Manage.Redemptions
        authorization = Utils.AuthRequired.USER
        endPoint ="//channel_points//custom_rewards"
    

class GetChanneliCalendarResponse(Utils.ResponseBaseClass):
        def __init__(self) -> None:
            super().__init__()

class UpdateChannelStreamScheduleRequest(Utils.RequestBaseClass):
        requestType = Utils.HTTPMethod.POST
        scope = Scope.Channel.Manage.Redemptions
        authorization = Utils.AuthRequired.USER
        endPoint ="//channel_points//custom_rewards"
    

class UpdateChannelStreamScheduleResponse(Utils.ResponseBaseClass):
        def __init__(self) -> None:
            super().__init__()

class CreateChannelStreamScheduleSegmentRequest(Utils.RequestBaseClass):
        requestType = Utils.HTTPMethod.POST
        scope = Scope.Channel.Manage.Redemptions
        authorization = Utils.AuthRequired.USER
        endPoint ="//channel_points//custom_rewards"
    

class CreateChannelStreamScheduleSegmentResponse(Utils.ResponseBaseClass):
        def __init__(self) -> None:
            super().__init__()

class UpdateChannelStreamScheduleSegmentRequest(Utils.RequestBaseClass):
        requestType = Utils.HTTPMethod.POST
        scope = Scope.Channel.Manage.Redemptions
        authorization = Utils.AuthRequired.USER
        endPoint ="//channel_points//custom_rewards"
    

class UpdateChannelStreamScheduleSegmentResponse(Utils.ResponseBaseClass):
        def __init__(self) -> None:
            super().__init__()

class DeleteChannelStreamScheduleSegmentRequest(Utils.RequestBaseClass):
        requestType = Utils.HTTPMethod.POST
        scope = Scope.Channel.Manage.Redemptions
        authorization = Utils.AuthRequired.USER
        endPoint ="//channel_points//custom_rewards"
    

class DeleteChannelStreamScheduleSegmentResponse(Utils.ResponseBaseClass):
        def __init__(self) -> None:
            super().__init__()