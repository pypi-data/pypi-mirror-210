from Twitch.API.Resources.__imports import *

class CheckAutoModStatusRequest(Utils.RequestBaseClass):
        requestType = Utils.HTTPMethod.POST
        scope = Scope.Channel.Manage.Redemptions
        authorization = Utils.AuthRequired.USER
        endPoint ="//channel_points//custom_rewards"
    

class CheckAutoModStatusResponse(Utils.ResponseBaseClass):
        def __init__(self) -> None:
            super().__init__()

class ManageHeldAutoModMessagesRequest(Utils.RequestBaseClass):
        requestType = Utils.HTTPMethod.POST
        scope = Scope.Channel.Manage.Redemptions
        authorization = Utils.AuthRequired.USER
        endPoint ="//channel_points//custom_rewards"
    

class ManageHeldAutoModMessagesResponse(Utils.ResponseBaseClass):
        def __init__(self) -> None:
            super().__init__()

class GetAutoModSettingsRequest(Utils.RequestBaseClass):
        requestType = Utils.HTTPMethod.POST
        scope = Scope.Channel.Manage.Redemptions
        authorization = Utils.AuthRequired.USER
        endPoint ="//channel_points//custom_rewards"
    

class GetAutoModSettingsResponse(Utils.ResponseBaseClass):
        def __init__(self) -> None:
            super().__init__()

class UpdateAutoModSettingsRequest(Utils.RequestBaseClass):
        requestType = Utils.HTTPMethod.POST
        scope = Scope.Channel.Manage.Redemptions
        authorization = Utils.AuthRequired.USER
        endPoint ="//channel_points//custom_rewards"
    

class UpdateAutoModSettingsResponse(Utils.ResponseBaseClass):
        def __init__(self) -> None:
            super().__init__()

class GetBannedUsersRequest(Utils.RequestBaseClass):
        requestType = Utils.HTTPMethod.POST
        scope = Scope.Channel.Manage.Redemptions
        authorization = Utils.AuthRequired.USER
        endPoint ="//channel_points//custom_rewards"
    

class GetBannedUsersResponse(Utils.ResponseBaseClass):
        def __init__(self) -> None:
            super().__init__()

class BanUserRequest(Utils.RequestBaseClass):
        requestType = Utils.HTTPMethod.POST
        scope = Scope.Channel.Manage.Redemptions
        authorization = Utils.AuthRequired.USER
        endPoint ="//channel_points//custom_rewards"
    

class BanUserResponse(Utils.ResponseBaseClass):
        def __init__(self) -> None:
            super().__init__()

class UnbanUserRequest(Utils.RequestBaseClass):
        requestType = Utils.HTTPMethod.POST
        scope = Scope.Channel.Manage.Redemptions
        authorization = Utils.AuthRequired.USER
        endPoint ="//channel_points//custom_rewards"
    

class UnbanUserResponse(Utils.ResponseBaseClass):
        def __init__(self) -> None:
            super().__init__()

class GetBlockedTermsRequest(Utils.RequestBaseClass):
        requestType = Utils.HTTPMethod.POST
        scope = Scope.Channel.Manage.Redemptions
        authorization = Utils.AuthRequired.USER
        endPoint ="//channel_points//custom_rewards"
    

class GetBlockedTermsResponse(Utils.ResponseBaseClass):
        def __init__(self) -> None:
            super().__init__()

class AddBlockedTermRequest(Utils.RequestBaseClass):
        requestType = Utils.HTTPMethod.POST
        scope = Scope.Channel.Manage.Redemptions
        authorization = Utils.AuthRequired.USER
        endPoint ="//channel_points//custom_rewards"
    

class AddBlockedTermResponse(Utils.ResponseBaseClass):
        def __init__(self) -> None:
            super().__init__()

class RemoveBlockedTermRequest(Utils.RequestBaseClass):
        requestType = Utils.HTTPMethod.POST
        scope = Scope.Channel.Manage.Redemptions
        authorization = Utils.AuthRequired.USER
        endPoint ="//channel_points//custom_rewards"
    

class RemoveBlockedTermResponse(Utils.ResponseBaseClass):
        def __init__(self) -> None:
            super().__init__()

class DeleteChatMessagesRequest(Utils.RequestBaseClass):
        requestType = Utils.HTTPMethod.POST
        scope = Scope.Channel.Manage.Redemptions
        authorization = Utils.AuthRequired.USER
        endPoint ="//channel_points//custom_rewards"
    

class DeleteChatMessagesResponse(Utils.ResponseBaseClass):
        def __init__(self) -> None:
            super().__init__()

class GetModeratorsRequest(Utils.RequestBaseClass):
        requestType = Utils.HTTPMethod.POST
        scope = Scope.Channel.Manage.Redemptions
        authorization = Utils.AuthRequired.USER
        endPoint ="//channel_points//custom_rewards"
    

class GetModeratorsResponse(Utils.ResponseBaseClass):
        def __init__(self) -> None:
            super().__init__()

class AddChannelModeratorRequest(Utils.RequestBaseClass):
        requestType = Utils.HTTPMethod.POST
        scope = Scope.Channel.Manage.Redemptions
        authorization = Utils.AuthRequired.USER
        endPoint ="//channel_points//custom_rewards"
    

class AddChannelModeratorResponse(Utils.ResponseBaseClass):
        def __init__(self) -> None:
            super().__init__()

class RemoveChannelModeratorRequest(Utils.RequestBaseClass):
        requestType = Utils.HTTPMethod.POST
        scope = Scope.Channel.Manage.Redemptions
        authorization = Utils.AuthRequired.USER
        endPoint ="//channel_points//custom_rewards"
    

class RemoveChannelModeratorResponse(Utils.ResponseBaseClass):
        def __init__(self) -> None:
            super().__init__()

class GetVIPsRequest(Utils.RequestBaseClass):
        requestType = Utils.HTTPMethod.POST
        scope = Scope.Channel.Manage.Redemptions
        authorization = Utils.AuthRequired.USER
        endPoint ="//channel_points//custom_rewards"
    

class GetVIPsResponse(Utils.ResponseBaseClass):
        def __init__(self) -> None:
            super().__init__()

class AddChannelVIPRequest(Utils.RequestBaseClass):
        requestType = Utils.HTTPMethod.POST
        scope = Scope.Channel.Manage.Redemptions
        authorization = Utils.AuthRequired.USER
        endPoint ="//channel_points//custom_rewards"
    

class AddChannelVIPResponse(Utils.ResponseBaseClass):
        def __init__(self) -> None:
            super().__init__()

class RemoveChannelVIPRequest(Utils.RequestBaseClass):
        requestType = Utils.HTTPMethod.POST
        scope = Scope.Channel.Manage.Redemptions
        authorization = Utils.AuthRequired.USER
        endPoint ="//channel_points//custom_rewards"
    

class RemoveChannelVIPResponse(Utils.ResponseBaseClass):
        def __init__(self) -> None:
            super().__init__()

class UpdateShieldModeStatusRequest(Utils.RequestBaseClass):
        requestType = Utils.HTTPMethod.POST
        scope = Scope.Channel.Manage.Redemptions
        authorization = Utils.AuthRequired.USER
        endPoint ="//channel_points//custom_rewards"
    

class UpdateShieldModeStatusResponse(Utils.ResponseBaseClass):
        def __init__(self) -> None:
            super().__init__()

class GetShieldModeStatusRequest(Utils.RequestBaseClass):
        requestType = Utils.HTTPMethod.POST
        scope = Scope.Channel.Manage.Redemptions
        authorization = Utils.AuthRequired.USER
        endPoint ="//channel_points//custom_rewards"
    

class GetShieldModeStatusResponse(Utils.ResponseBaseClass):
        def __init__(self) -> None:
            super().__init__()
