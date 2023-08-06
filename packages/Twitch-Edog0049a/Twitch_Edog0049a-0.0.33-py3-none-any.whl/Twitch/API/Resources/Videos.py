from Twitch.API.Resources.__imports import *
class GetVideosRequest(Utils.RequestBaseClass):
    requestType = Utils.HTTPMethod.GET
    scope = Scope.Channel.Manage.Videos
    authorization = Utils.AuthRequired.USER
    endPoint ="/videos"
    def __init__(self, id: Optional[str]=None, user_id: Optional[str]=None, 
            game_id: Optional[str]=None, language: Optional[str]=None, 
            period: Optional[str]=None, sort: Optional[str]=None, 
            type: Optional[str]=None, first: Optional[str]=None, 
            after: Optional[str]=None, before: Optional[str]=None) -> None:
        self.id = id
        self.user_id = user_id
        self.game_id = game_id
        self.language = language
        self.period = period
        self.sort = sort
        self.type = type
        self.first = first
        self.after = after
        self.before = before
        super().__init__()


class MutedSegment:
    duration: int
    offset: int


class VideoItem:
    id: str
    stream_id: str
    user_id: str
    user_login: str
    user_name: str
    title: str
    description: str
    created_at: str
    published_at: str
    url: str
    thumbnail_url: str
    viewable: str
    view_count: str
    language: str
    type: str
    duration: str
    muted_segments: MutedSegment	

class GetVideosResponse(Utils.PagenationMixin, Utils.ResponseBaseClass):
    def __init__(self) -> None:
        super().__init__(VideoItem)


class DeleteVideosRequest(Utils.RequestBaseClass):
    requestType = Utils.HTTPMethod.DELETE
    scope = Scope.Channel.Manage.Videos
    authorization = Utils.AuthRequired.USER
    endPoint ="/videos"
    def __init__(self, id: str | list) -> None:
        ids: list = list
        if isinstance(id,list):
            for item in id:
                ids.append(("id",id))
            id = ids       
        super().__init__()


class DeleteVideoItem:
     id: str
class DeleteVideosResponse(Utils.ResponseBaseClass):
        def __init__(self) -> None:
            super().__init__(DeleteVideoItem)
