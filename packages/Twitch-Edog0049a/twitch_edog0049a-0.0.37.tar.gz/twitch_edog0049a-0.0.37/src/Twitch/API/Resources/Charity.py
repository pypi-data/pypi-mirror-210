from Twitch.API.Resources.__imports import *

"""
Get Charity Campaign
"""
class GetCharityCampaignRequest(Utils.RequestBaseClass):
    requestType = Utils.HTTPMethod.GET
    scope = Scope.Channel.Read.Charity
    authorization = Utils.AuthRequired.USER
    endPoint ="/charity/campaigns"
    def __init__(self, broadcaster_id) -> None:
          self.broadcaster_id = broadcaster_id
          super().__init__()
          
class Amount:
    value: int
    decimal_places: int
    currency: str 

class CharityCampaignItem:
    id: str
    broadcaster_id: str
    broadcaster_login: str
    broadcaster_name: str
    charity_name: str
    charity_description: str
    charity_logo: str 
    charity_website: str
    current_amount: Amount
    target_amount: Amount

"""
Get Charity Campaign Donations
"""
class GetCharityCampaignDonationsRequest(Utils.PagenationMixin, Utils.RequestBaseClass):
    requestType = Utils.HTTPMethod.GET
    scope = Scope.Channel.Read.Charity
    authorization = Utils.AuthRequired.USER
    endPoint ="/charity/donations"
    def __init__(self, broadcaster_id: str, first: Optional[int]=None, after:Optional[str]=None) -> None:
        self.broadcaster_id = broadcaster_id
        self.first = first
        self.after = after
        super().__init__()

class GetCharityCampaignResponse(Utils.ResponseBaseClass):
    def __init__(self) -> None:
        super().__init__(CharityCampaignItem)
class CampaignDonationItem:
    id: str
    campaign_id: str
    user_id: str
    user_login: str
    user_name: str
    amount: Amount

class GetCharityCampaignDonationsResponse(Utils.ResponseBaseClass):
    def __init__(self) -> None:
        super().__init__(CampaignDonationItem)