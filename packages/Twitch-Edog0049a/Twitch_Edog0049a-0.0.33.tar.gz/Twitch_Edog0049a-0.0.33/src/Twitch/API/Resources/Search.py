from Twitch.API.Resources.__imports import *

class SearchCategoriesRequest(Utils.RequestBaseClass):
        requestType = Utils.HTTPMethod.POST
        scope = Scope.Channel.Manage.Redemptions
        authorization = Utils.AuthRequired.USER
        endPoint ="//channel_points//custom_rewards"
    

class SearchCategoriesResponse(Utils.ResponseBaseClass):
        def __init__(self) -> None:
            super().__init__()

class SearchChannelsRequest(Utils.RequestBaseClass):
        requestType = Utils.HTTPMethod.POST
        scope = Scope.Channel.Manage.Redemptions
        authorization = Utils.AuthRequired.USER
        endPoint ="//channel_points//custom_rewards"
    

class SearchChannelsResponse(Utils.ResponseBaseClass):
        def __init__(self) -> None:
            super().__init__()