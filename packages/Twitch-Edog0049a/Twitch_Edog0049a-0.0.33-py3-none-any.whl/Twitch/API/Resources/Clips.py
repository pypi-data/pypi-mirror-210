from Twitch.API.Resources.__imports import *
class CreateClipRequest(Utils.RequestBaseClass):
    requestType = Utils.HTTPMethod.POST
    scope = Scope.Clips.Edit
    authorization = Utils.AuthRequired.USER
    endPoint ="/clips"
    def __init__(self, broadcaster_id: str, has_delay: Optional[bool]=None) -> None:
        self.broadcaster_id = broadcaster_id
        self.has_delay = has_delay
        super().__init__()
class NewClipItem:
    edit_url: str
    id: str
class CreateClipResponse(Utils.ResponseBaseClass):
    def __init__(self) -> None:
        super().__init__(NewClipItem)

class GetClipsRequest(Utils.RequestBaseClass):
    requestType = Utils.HTTPMethod.GET
    scope = None
    authorization = Utils.AuthRequired.CLIENT
    endPoint ="/clips"
    def __init__(self, broadcaster_id: Optional[str]=None, 
                 game_id: Optional[str]=None, id: Optional[str]=None, 
                 started_at: Optional[str]=None, ended_at: Optional[str]=None, 
                 first: Optional[str]=None, before: Optional[str]=None, after: Optional[str]=None) -> None:
        self.broadcaster_id = broadcaster_id
        self.game_id = game_id
        self.id = id
        self.started_at = started_at
        self.ended_at = ended_at
        self.first = first
        self.before = before
        self.after = after
        super().__init__()
    
class ClipItem:
    id: str 
    url: str 
    embed_url: str 
    broadcaster_id: str 
    broadcaster_name: str 
    creator_id: str 
    creator_name: str 
    video_id: str 
    game_id: str 
    language: str 
    title: str 
    view_count: int 
    created_at: str 
    thumbnail_url: str 
    duration: float
    vod_offset: int 
class GetClipsResponse(Utils.PagenationMixin, Utils.ResponseBaseClass):
        def __init__(self) -> None:
            super().__init__(ClipItem)
