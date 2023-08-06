from Twitch.API.Resources.__imports import *

class GetSoundtrackCurrentTrackRequest(Utils.RequestBaseClass):
        requestType = Utils.HTTPMethod.POST
        scope = Scope.Channel.Manage.Redemptions
        authorization = Utils.AuthRequired.USER
        endPoint ="//channel_points//custom_rewards"
    

class GetSoundtrackCurrentTrackResponse(Utils.ResponseBaseClass):
        def __init__(self) -> None:
            super().__init__()

class GetSoundtrackPlaylistRequest(Utils.RequestBaseClass):
        requestType = Utils.HTTPMethod.POST
        scope = Scope.Channel.Manage.Redemptions
        authorization = Utils.AuthRequired.USER
        endPoint ="//channel_points//custom_rewards"
    

class GetSoundtrackPlaylistResponse(Utils.ResponseBaseClass):
        def __init__(self) -> None:
            super().__init__()

class GetSoundtrackPlaylistsRequest(Utils.RequestBaseClass):
        requestType = Utils.HTTPMethod.POST
        scope = Scope.Channel.Manage.Redemptions
        authorization = Utils.AuthRequired.USER
        endPoint ="//channel_points//custom_rewards"
    

class GetSoundtrackPlaylistsResponse(Utils.ResponseBaseClass):
        def __init__(self) -> None:
            super().__init__()
