from Twitch.API.Resources.__imports import *

class GetUsersRequest(Utils.RequestBaseClass):
    requestType = Utils.HTTPMethod.GET
    scope = Scope.User.Read.Email
    authorization = Utils.AuthRequired.CLIENT
    endPoint ="/users"
    def __init__(self, id:Optional[str|list] = None, login: Optional[str|list]=None) -> None:
            self.id =   id  
            self.login = login
            super().__init__()

class UserItem:
    id: str 
    login: str 
    display_name: str 
    type: str
    broadcaster_type: str 
    description: str
    profile_image_url: str
    offline_image_url: str 
    view_count: int
    email: str
    created_at: str

class GetUsersResponse(Utils.ResponseBaseClass):
    def __init__(self) -> None:
        super().__init__(UserItem)

class UpdateUserRequest(Utils.RequestBaseClass):
    requestType = Utils.HTTPMethod.PUT
    scope = Scope.User.Read.Email
    authorization = Utils.AuthRequired.USER
    endPoint ="/users"
    def __init__(self, description: str) -> None:
        super().__init__()


class UpdateUserResponse(Utils.ResponseBaseClass):
    def __init__(self) -> None:
        super().__init__(UserItem)


class GetUserBlockListRequest(Utils.RequestBaseClass):
    requestType = Utils.HTTPMethod.POST
    scope = Scope.Channel.Manage.Redemptions
    authorization = Utils.AuthRequired.USER
    endPoint ="/users"
    

class GetUserBlockListResponse(Utils.ResponseBaseClass):
    def __init__(self) -> None:
        super().__init__()

class BlockUserRequest(Utils.RequestBaseClass):
    requestType = Utils.HTTPMethod.POST
    scope = Scope.Channel.Manage.Redemptions
    authorization = Utils.AuthRequired.USER
    endPoint ="/users"
    

class BlockUserResponse(Utils.ResponseBaseClass):
    def __init__(self) -> None:
        super().__init__()

class UnblockUserRequest(Utils.RequestBaseClass):
    requestType = Utils.HTTPMethod.POST
    scope = Scope.Channel.Manage.Redemptions
    authorization = Utils.AuthRequired.USER
    endPoint ="/users"


class UnblockUserResponse(Utils.ResponseBaseClass):
    def __init__(self) -> None:
        super().__init__()

class GetUserExtensionsRequest(Utils.RequestBaseClass):
    requestType = Utils.HTTPMethod.POST
    scope = Scope.Channel.Manage.Redemptions
    authorization = Utils.AuthRequired.USER
    endPoint ="/users"
    

class GetUserExtensionsResponse(Utils.ResponseBaseClass):
    def __init__(self) -> None:
        super().__init__()

class GetUserActiveExtensionsRequest(Utils.RequestBaseClass):
    requestType = Utils.HTTPMethod.POST
    scope = Scope.Channel.Manage.Redemptions
    authorization = Utils.AuthRequired.USER
    endPoint ="/users"
    

class GetUserActiveExtensionsResponse(Utils.ResponseBaseClass):
    def __init__(self) -> None:
        super().__init__()

class UpdateUserExtensionsRequest(Utils.RequestBaseClass):
    requestType = Utils.HTTPMethod.POST
    scope = Scope.Channel.Manage.Redemptions
    authorization = Utils.AuthRequired.USER
    endPoint ="/users"
    

class UpdateUserExtensionsResponse(Utils.ResponseBaseClass):
    def __init__(self) -> None:
        super().__init__()

