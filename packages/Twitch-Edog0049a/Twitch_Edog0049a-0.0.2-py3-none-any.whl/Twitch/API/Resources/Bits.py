from Twitch.API.Resources.__imports import *

"""
Get Bits Leaderboard
"""

class GetBitsLeaderboardRequest(Utils.RequestBaseClass):
    requestType = Utils.HTTPMethod.GET
    scope = Scope.Bits.Read
    authorization = Utils.AuthRequired.USER
    endPoint = "/bits/leaderboard"

    def __init__(self, count: Optional[int]=None, 
                 period: Optional[str]=None, 
                 started_at: Optional[datetime]=None, 
                 user_id: Optional[str]=None
                ) -> None:
        
        self.count: int = count
        self.period: str = period
        self.started_at: str = started_at.isoformat("T") if isinstance(started_at, datetime) else started_at
        self.user_id: str = user_id
        super().__init__()

class BitsLeaderboardItem:
    def __init__(self) -> None:
        self.user_id:str = ""
        self.user_login:str = ""
        self.user_name:str = ""
        self.rank: int = -1
        self.score: int = -1

class GetBitsLeaderboardResponse(Utils.DateRangeMixin, Utils.ResponseBaseClass):
    def __init__(self) -> None:
        super().__init__(BitsLeaderboardItem)
   


"""
Get Cheermotes
"""

class GetCheermotesRequest(Utils.RequestBaseClass):
    requestType = Utils.HTTPMethod.GET
    scope = None
    authorization = Utils.AuthRequired.CLIENT 
    endPoint = "/bits/cheermotes"
    def __init__(self,broadcaster_id:Optional[str] = None, userAuth: bool=False) -> None:
        if userAuth:
            self.authorization = Utils.AuthRequired.USER

        self.broadcaster_id = broadcaster_id
        super().__init__()

class ImageItem:
    animated : dict[str,str] = []
    static: dict[str,str] = []

class ImagesItem:
    dark: ImageItem = None
    light: ImageItem = None

class teirItem:
    min_bits: int = -1
    id: str = ""
    color: str = ""
    images: ImagesItem = None
    can_cheer: bool = False
    show_in_bits_card: bool =  False

class CheermotesItem:
    prefix: str = ""
    _tiers: list[teirItem] = list()
    type: str = ""
    order: int = -1
    last_updated: str = ""
    is_charitable: bool = False
    
    @property
    def tiers(self)->list[teirItem]:
        return self._tiers
    
    @tiers.setter
    def tiers(self,tiersList) -> None:
        for item in tiersList:
            tmpItem = teirItem()
            for key, value in item.items():
                tmpItem.__setattr__(key,value)
            self._tiers.append(tmpItem)



    
class GetCheermotesResponse(Utils.ResponseBaseClass):
    def __init__(self,) -> None:
        super().__init__(CheermotesItem)

"""
Get Extension Transactions
"""

class GetExtensionTransactionsRequest(Utils.RequestBaseClass):
    requestType = Utils.HTTPMethod.GET
    scope = None
    authorization = Utils.AuthRequired.CLIENT
    endPoint = "/extensions/transactions"

    def __init__(self, extension_id: str, id: Optional[str]=None, first: Optional[int]=None, after: Optional[str] = None) -> None:
        self.extension_id: str = extension_id
        self.id: Optional[str] = id 
        self.first: Optional[int] = first
        self.after: Optional[str] = after
        super().__init__()

class ProductDataItem:
    domain: str = ""
    sku: str =""
    inDevelopment: bool = False,
    displayName: str = ""
    expiration:str = ""
    broadcast:bool = False   
    class cost: 
        amount: int = 0
        type: str = ""
     
class ExtensionTransactionItem:
    id: str = "",
    timestamp: str = ""
    broadcaster_id: str = ""
    broadcaster_login: str = ""
    broadcaster_name: str = ""
    user_id: str = ""
    user_login: str = ""
    user_name: str = ""
    product_type: str = ""
    product_data: ProductDataItem 

class GetExtensionTransactionsResponse(Utils.PagenationMixin, Utils.ResponseBaseClass):
    def __init__(self) -> None:
        super().__init__(ExtensionTransactionItem)