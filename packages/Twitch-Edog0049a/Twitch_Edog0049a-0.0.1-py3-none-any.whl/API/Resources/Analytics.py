from Twitch.API.Resources.__imports import *
"""
Get Extension Analytics
"""

class GetExtensionAnalyticsRequest(Utils.RequestBaseClass):
    requestType = Utils.HTTPMethod.GET
    scope = Scope.Analytics.Read.Extensions
    authorization = Utils.AuthRequired.USER
    endPoint = "/analytics/extensions"

    def __init__(self, 
                extension_id: Optional[str]= None, 
                type: Optional[str]= None,
                started_at: Optional[datetime] = None,
                ended_at: Optional[datetime] = None,
                first: Optional[int] = None,
                after: Optional[str] = None
                    ) -> None:
        
        self.extension_id = extension_id
        self.type = type
        self.started_at = started_at.isoformat("T") if isinstance(started_at, datetime) else started_at
        self.ended_at = ended_at.isoformat("T") if isinstance(ended_at, datetime) else started_at
        self.first = first
        self.after = after 
        super().__init__()

class ExtensionAnalyticsItem(Utils.DateRangeMixin):
    extension_id:str
    URL:str
    type:str

class GetExtensionAnalyticsResponse(Utils.PagenationMixin, Utils.ResponseBaseClass):
    def __init__(self) -> None:
        super().__init__(ExtensionAnalyticsItem)

"""
Get Game Analytics
"""   
class GetGameAnalyticsRequest(Utils.RequestBaseClass):
    requestType = Utils.HTTPMethod.GET
    scope = Scope.Analytics.Read.Extensions
    authorization = Utils.AuthRequired.USER
    endPoint = "/analytics/extensions"
    game_id: str
    date_range: Utils.dateRange

    def __init__(self, 
                 game_id: Optional[str] = None,
                 type: Optional[str]= None,
                 started_at: Optional[datetime] = None,
                 ended_at: Optional[datetime] = None,
                 first: Optional[int] = None,
                 after: Optional[str] = None
                    ) -> None:
        
        self.game_id = game_id
        self.type = type
        self.started_at = started_at.isoformat("T") if isinstance(started_at, datetime) else started_at
        self.ended_at = ended_at.isoformat("T") if isinstance(ended_at, datetime) else started_at
        self.first = first
        self.after = after 
        super().__init__()

class GameAnalyticsItem(Utils.DateRangeMixin):
    def __init__(self) -> None:
        self.game_id:str
        self.URL:str
        self.type:str
class GetGameAnalyticsResponse(Utils.PagenationMixin, Utils.ResponseBaseClass):
    def __init__(self) -> None:
        super().__init__(GameAnalyticsItem)