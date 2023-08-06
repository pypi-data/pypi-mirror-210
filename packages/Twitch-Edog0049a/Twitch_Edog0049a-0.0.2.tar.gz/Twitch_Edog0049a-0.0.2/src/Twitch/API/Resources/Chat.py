from Twitch.API.Resources.__imports import *

"""
Get Chatters
"""
class GetChattersRequest(Utils.RequestBaseClass):
        requestType = Utils.HTTPMethod.GET
        scope = Scope.Moderator.Read.Chatters
        authorization = Utils.AuthRequired.USER
        endPoint ="/chat/chatters"
        def __init__(self, broadcaster_id:str, moderator_id:str, first: Optional[int]= None, after: Optional[str]=None ) -> None:
              self.broadcaster_id = broadcaster_id
              self.moderator_id = moderator_id
              self.first = first
              self.after = after
              super().__init__()
    
class ChatterItem:
    user_id: str 
    user_login: str 
    user_name: str 
class GetChattersResponse(Utils.PagenationMixin, Utils.ResponseBaseClass):
    total: int
    def __init__(self) -> None:
        super().__init__(ChatterItem)

"""
Get Channel Emotes
"""
class GetChannelEmotesRequest(Utils.RequestBaseClass):
        requestType = Utils.HTTPMethod.GET
        scope = None
        authorization = Utils.AuthRequired.CLIENT
        endPoint ="/chat/emotes"
        def __init__(self, broadcaster_id: str, userAuth: bool=False ) -> None:
              if userAuth:
                    self.authorization = Utils.AuthRequired.USER
              super().__init__()

class Images:
    url_1x: str 
    url_2x: str 
    url_4x: str 

class ChannelEmoteItem:
    id: str 
    name: str 
    images: Images 
    tier: str 
    emote_type: str 
    emote_set_id: str 
    format: list[str] 
    scale: list[str] 
    theme_mode: list[str] 
    template: str 

class GetChannelEmotesResponse(Utils.ResponseBaseClass):
    def __init__(self) -> None:
        super().__init__(ChannelEmoteItem)

"""
Get Global Emotes
"""
class GetGlobalEmotesRequest(Utils.RequestBaseClass):
    requestType = Utils.HTTPMethod.GET
    scope = None
    authorization = Utils.AuthRequired.CLIENT
    endPoint ="/chat/emotes/global"
    def __init__(self, userAuth: bool=False) -> None:
        if userAuth:
            self.authorization = Utils.AuthRequired.USER
        super().__init__()
    
class GlobalEmoteItem:
    id: str 
    name: str 
    images: Images
    format: list[str] 
    scale: list[str] 
    theme_mode: list[str] 

class GetGlobalEmotesResponse(Utils.ResponseBaseClass):
    template: str
    def __init__(self) -> None:
        super().__init__(GlobalEmoteItem)

"""
Get Emote Sets
"""

class GetEmoteSetsRequest(Utils.RequestBaseClass):
    requestType = Utils.HTTPMethod.GET
    scope = None
    authorization = Utils.AuthRequired.CLIENT
    endPoint ="/chat/emotes/set"
    def __init__(self, emote_set_id: str, userAuth: bool=False ) -> None:
        if userAuth:
            self.authorization.USER
        self.emote_set_id = emote_set_id    
        super().__init__()

class EmoteSetItem:
    id: str 
    name: str 
    images: Images
    emote_type: str 
    emote_set_id: str 
    owner_id: str 
    format: list[str] 
    scale: list[str] 
    theme_mode: list[str] 

class GetEmoteSetsResponse(Utils.ResponseBaseClass):
        template: str
        def __init__(self) -> None:
            super().__init__(EmoteSetItem)
            
"""
Get Channel Chat Badges
"""
class GetChannelChatBadgesRequest(Utils.RequestBaseClass):
    requestType = Utils.HTTPMethod.GET
    scope = None
    authorization = Utils.AuthRequired.CLIENT
    endPoint ="/chat/badges"
    def __init__(self, broadcaster_id: str, userAuth: bool=False) -> None:
        if userAuth:
             self.authorization = Utils.AuthRequired.USER
        self.broadcaster_id = broadcaster_id
        super().__init__()
class Version:
    id: str 
    image_url_1x: str 
    image_url_2x: str 
    image_url_4x: str 
    title: str 
    description: str 
    click_action: str 
    click_url: str 
class ChatBadgeItem:
    set_id: str 
    versions: list[Version]     

class GetChannelChatBadgesResponse(Utils.ResponseBaseClass):
        def __init__(self) -> None:
            super().__init__(ChatBadgeItem)

"""
Get Global Chat Badges
"""
class GetGlobalChatBadgesRequest(Utils.RequestBaseClass):
    requestType = Utils.HTTPMethod.GET
    scope = None
    authorization = Utils.AuthRequired.CLIENT
    endPoint ="/chat/badges/global"
    def __init__(self, userAuth: bool=False) -> None:
        if userAuth:
            self.authorization = Utils.AuthRequired.USER
        super().__init__()


class GetGlobalChatBadgesResponse(Utils.ResponseBaseClass):
        def __init__(self) -> None:
            super().__init__(ChatBadgeItem)


"""
Get Chat Settings
"""
class GetChatSettingsRequest(Utils.RequestBaseClass):
    requestType = Utils.HTTPMethod.GET
    scope = None
    authorization = Utils.AuthRequired.CLIENT
    endPoint ="chat/settings"
    def __init__(self, broadcaster_id: str, moderator_id:Optional[str] = None) -> None:
        if moderator_id is not None:
            self.authorization = Utils.AuthRequired.USER
        
        self.broadcaster_id = broadcaster_id
        self.moderator_id = moderator_id
        super().__init__()

    
class ChatSettingsItem:
    broadcaster_id: str 
    emote_mode: bool 
    follower_mode: bool 
    follower_mode_duration: int 
    moderator_id: str 
    non_moderator_chat_delay: bool 
    non_moderator_chat_delay_duration: int 
    slow_mode: bool 
    slow_mode_wait_time: int 
    subscriber_mode: bool 
    unique_chat_mode: bool 
class GetChatSettingsResponse(Utils.ResponseBaseClass):
        def __init__(self) -> None:
            super().__init__(ChatSettingsItem)

"""
Update Chat Settings
"""
class UpdateChatSettingsRequest(Utils.RequestBaseClass):
    requestType = Utils.HTTPMethod.PATCH
    scope = Scope.Moderator.Manage.Chat_settings
    authorization = Utils.AuthRequired.USER
    endPoint ="/chat/settings"
    def __init__(self, 
                broadcaster_id: str, 
                moderator_id: str,
                emote_mode: Optional[bool]=None,
                follower_mode: Optional[bool]=None,
                follower_mode_duration: Optional[int]=None,
                non_moderator_chat_delay: Optional[bool]=None,
                non_moderator_chat_delay_duration: Optional[bool]=None,
                slow_mode:Optional[bool]=None,
                slow_mode_wait_time: Optional[bool]=None,
                subscriber_mode: Optional[bool]=None, 
                unique_chat_mode: Optional[bool]=None 
                    ) -> None:
        self.broadcaster_id = broadcaster_id
        self.moderator_id = moderator_id
        self.emote_mode = emote_mode
        self.follower_mode = follower_mode
        self.follower_mode_duration = follower_mode_duration
        self.non_moderator_chat_delay = non_moderator_chat_delay_duration
        self.non_moderator_chat_delay_duration = non_moderator_chat_delay_duration 
        self.slow_mode = slow_mode 
        self.slow_mode_wait_time = slow_mode_wait_time
        self.subscriber_mode = subscriber_mode
        self.unique_chat_mode = unique_chat_mode
        super().__init__()

class UpdateChatSettingsResponse(Utils.ResponseBaseClass):
    def __init__(self) -> None:
         super().__init__(ChatSettingsItem)

"""
Send Chat Announcement
"""

class SendChatAnnouncementRequest(Utils.RequestBaseClass):
    requestType = Utils.HTTPMethod.POST
    scope = Scope.Moderator.Manage.Announcements
    authorization = Utils.AuthRequired.USER
    endPoint ="/chat/announcements"
    def __init__(self, broadcaster_id: str, moderator_id: str, message: str, color: Optional[str]=None) -> None:
        self.broadcaster_id = broadcaster_id
        self.moderator_id = moderator_id
        self.message = message 
        self.color = color
        super().__init__()
    

class SendChatAnnouncementResponse(Utils.ResponseBaseClass):
        def __init__(self) -> None:
            super().__init__(None)


"""
Send a Shoutout
"""
class SendaShoutoutRequest(Utils.RequestBaseClass):
    requestType = Utils.HTTPMethod.POST
    scope = Scope.Moderator.Manage.Shoutouts
    authorization = Utils.AuthRequired.USER
    endPoint ="chat/shoutouts"
    def __init__(self, from_broadcaster_id: str, to_broadcaster_id: str, moderator_id: str) -> None:
        self.from_broadcaster_id = from_broadcaster_id
        self.to_broadcaster_id = to_broadcaster_id
        self.moderator_id = moderator_id
        super().__init__()

class SendaShoutoutResponse(Utils.ResponseBaseClass):
        def __init__(self) -> None:
            super().__init__(None)

"""
Get User Chat Color
"""
class GetUserChatColorRequest(Utils.RequestBaseClass):
    requestType = Utils.HTTPMethod.GET
    scope = Scope.Channel.Manage.Redemptions
    authorization = Utils.AuthRequired.CLIENT
    endPoint ="/chat/color"
    def __init__(self, user_id: list[str], userAuth: bool=False) -> None:
        if userAuth:
            self.authorization = Utils.AuthRequired.USER
        self.user_id = user_id
        super().__init__()

class UserChatColor:
    user_id: str 
    user_login: str 
    user_name: str 
    color: str 
    edit_url: str 
    id: str 
 
class GetUserChatColorResponse(Utils.ResponseBaseClass):
    def __init__(self) -> None:
        super().__init__(UserChatColor)


"""
Update User Chat Color
"""
class UpdateUserChatColorRequest(Utils.RequestBaseClass):
    requestType = Utils.HTTPMethod.PUT
    scope = Scope.User.Manage.Chat_color
    authorization = Utils.AuthRequired.USER
    endPoint ="/chat/color"
    def __init__(self, user_id: str, color: str) -> None:
          self.user_id = user_id
          self.color = color
          super().__init__()
    
class UpdateUserChatColorResponse(Utils.ResponseBaseClass):
    def __init__(self) -> None:
        super().__init__(None)