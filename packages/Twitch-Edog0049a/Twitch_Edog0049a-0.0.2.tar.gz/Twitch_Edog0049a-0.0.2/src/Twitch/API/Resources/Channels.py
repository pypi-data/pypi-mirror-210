from Twitch.API.Resources.__imports import *
"""
Get Channel Information
"""

class GetChannelInformationRequest(Utils.RequestBaseClass):
    requestType = Utils.HTTPMethod.GET
    scope = None
    authorization = Utils.AuthRequired.CLIENT
    endPoint = "/channels"
    def __init__(self, broadcaster_ids: list[str], userAuth: bool=False) -> None:
        if userAuth:
            self.authorization = Utils.AuthRequired.USER
  
        self.broadcaster_ids: list[str] = broadcaster_ids
        super().__init__()

class ChannelInformationItem:
    broadcaster_id: str
    broadcaster_login: str
    broadcaster_name: str
    broadcaster_language: str
    game_name: str
    game_id: str
    title: str
    delay: int
    tags: list

class GetChannelInformationResponse(Utils.ResponseBaseClass):
   def __init__(self) -> None:
       super().__init__(ChannelInformationItem) 

"""
Modify Channel Information
"""

class ModifyChannelInformationRequest(Utils.RequestBaseClass):
    requestType = Utils.HTTPMethod.PATCH
    scope = Scope.Channel.Manage.Broadcast
    authorization = Utils.AuthRequired.USER
    endPoint = "/channels"

    def __init__(self,
                 broadcaster_id: str,
                 game_id:Optional[str] =None,
                 broadcaster_language:Optional[str]=None,
                 title:Optional[str]=None,
                 delay:Optional[int]=None,
                 tags:Optional[list[str]]=None
                 ) -> None:
        self.broadcaster_id = broadcaster_id
        self.game_id = game_id
        self.broadcaster_language = broadcaster_language
        self.title = title
        self.delay = delay
        self.tags = tags
        super().__init__()

class ModifyChannelItem:
    status: Utils.HTTPMethod
class ModifyChannelInformationResponse(Utils.ResponseBaseClass):
    def __init__(self) -> None:
        super().__init__(ModifyChannelItem)


"""
Get Channel Editors
"""
class GetChannelEditorsRequest(Utils.RequestBaseClass):
    requestType = Utils.HTTPMethod.GET
    scope = Scope.Channel.Read.Editors
    authorization = Utils.AuthRequired.USER
    endPoint = "/channels/editors"

    def __init__(self, broadcaster_id: str) -> None:
        self.broadcaster_id = broadcaster_id
        super().__init__()

class ChannelEditorItem:
    user_id:str
    user_name: str
    created_at: str

class GetChannelEditorsResponse(Utils.ResponseBaseClass):
    def __init__(self) -> None:
        super().__init__(ChannelEditorItem)

"""
Get Followed Channels - BETA
"""
class GetFollowedChannelsRequest(Utils.RequestBaseClass):
    requestType = Utils.HTTPMethod.GET
    scope = Scope.User.Read.Follows
    authorization = Utils.AuthRequired.USER
    endPoint ="channels/followed"
    def __init__(self, user_id: str, 
                 broadcaster_id: Optional[str]=None, 
                 first: Optional[int]=None, 
                 after:Optional[str]=None) -> None:
        
        self.user_id: str = user_id
        self.broadcaster_id: str = broadcaster_id
        self.first: int = first
        self.after: str = after
        super().__init__()


class FollowedChannelItem:
    broadcaster_id: str
    broadcaster_login: str
    broadcaster_name: str
    followed_at: str 

class GetFollowedChannelsResponse(Utils.PagenationMixin, Utils.ResponseBaseClass):
    total:int = 0
    def __init__(self) -> None:
        super().__init__(FollowedChannelItem)

   
"""
Get Channel Followers - BETA
"""

class GetChannelFollowersRequest(Utils.RequestBaseClass):
    requestType = Utils.HTTPMethod.GET
    scope = Scope.Moderator.Read.Followers
    authorization = Utils.AuthRequired.USER
    endPoint = "/channels/followers"
    def __init__(self, broadcaster_id: str, 
                 user_id: Optional[str]=None, 
                 first: Optional[int]=None,  
                 after: Optional[str]=None) -> None:
        self.broadcaster_id: str = broadcaster_id
        self.user_id: str = user_id
        self.first: int = first
        self.after: str = after
        super().__init__()

class ChannelFollowerItem:
    followed_at: str    #UTC timestamp
    user_id: str        #ID that uniquely identifies the user that’s following the broadcaster.
    user_login: str     #user’s login name.
    user_name: str      #user’s display name.

class GetChannelFollowersResponse(Utils.PagenationMixin,Utils.ResponseBaseClass):
    total: int = 0
    def __init__(self) -> None:
        super().__init__(ChannelFollowerItem)