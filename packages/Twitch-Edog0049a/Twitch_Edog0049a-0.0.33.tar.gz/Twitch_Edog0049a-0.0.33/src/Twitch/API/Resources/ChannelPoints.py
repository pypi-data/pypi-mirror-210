from Twitch.API.Resources.__imports import *

"""
Create Custom Rewards
"""
class  MaxPerStreamSetting:
    is_enabled: bool
    max_per_stream: int

class MaxPerUserPerStreamSetting:
    is_enabled: bool
    max_per_user_per_stream: int

class GlobalCoolDownSetting:
    is_enabled: bool
    global_cooldown_seconds: int

class CustomRewardsImageItem:
    url_1x: str
    url_2x: str
    url_4x: str

class CreateCustomRewardsRequest(Utils.RequestBaseClass):
    requestType = Utils.HTTPMethod.POST
    scope = Scope.Channel.Manage.Redemptions
    authorization = Utils.AuthRequired.USER
    endPoint ="/channel_points/custom_rewards"
    def __init__(self, broadcaster_id: str, 
                 title: str,
                 cost: int,
                 prompt: Optional[str]=None,
                 is_enabled: Optional[bool]=None,
                 background_color: Optional[str]=None,
                 is_user_input_required: Optional[bool]=None,
                 is_max_per_stream_enabled: Optional[bool]=None,
                 max_per_stream: Optional[int]=None,
                 is_max_per_user_per_stream_enabled: Optional[bool]=None,
                 max_per_user_per_stream: Optional[int]=None,
                 is_global_cooldown_enabled: Optional[bool]=None,
                 global_cooldown_seconds: Optional[int]=None,
                 should_redemptions_skip_request_queue: Optional[bool]=None) -> None:    
        self.broadcaster_id = broadcaster_id
        self.title: str = title
        self.cost: int = cost
        self.prompt: Optional[str] = prompt
        self.is_enabled: Optional[bool]= is_enabled
        self.background_color: Optional[str] = background_color
        self.is_user_input_required: Optional[bool] = is_user_input_required
        self.is_max_per_stream_enabled: Optional[bool] = is_max_per_stream_enabled
        self.max_per_stream: Optional[int] = max_per_stream
        self.is_max_per_user_per_stream_enabled: Optional[bool] = is_max_per_user_per_stream_enabled
        self.max_per_user_per_stream: Optional[int] = max_per_user_per_stream
        self.is_global_cooldown_enabled: Optional[bool] = is_global_cooldown_enabled
        self.global_cooldown_seconds: Optional[int] = global_cooldown_seconds
        self.should_redemptions_skip_request_queue: Optional[bool] = should_redemptions_skip_request_queue
        super().__init__()

class CustomRewardsItem:
    broadcaster_id: str
    broadcaster_login: str
    broadcaster_name: str
    id: str
    title: str
    prompt: str
    cost: int
    image: CustomRewardsImageItem
    default_image: CustomRewardsImageItem
    background_color: str
    is_enabled: bool
    is_user_input_required: bool
    max_per_stream_setting: MaxPerStreamSetting
    max_per_user_per_stream_setting: MaxPerUserPerStreamSetting
    global_cooldown_setting: GlobalCoolDownSetting
    is_paused: bool
    is_in_stock: bool
    should_redemptions_skip_request_queue: bool
    redemptions_redeemed_current_stream: int
    cooldown_expires_at: str

class CreateCustomRewardsResponse(Utils.ResponseBaseClass):
    def __init__(self) -> None:
        super().__init__(CustomRewardsItem)

"""
Delete Custom Reward
"""
class DeleteCustomRewardRequest(Utils.RequestBaseClass):
    requestType = Utils.HTTPMethod.DELETE
    scope = Scope.Channel.Manage.Redemptions
    authorization = Utils.AuthRequired.USER
    endPoint ="/channel_points/custom_rewards"
    def __init__(self,broadcaster_id: str, id: str) -> None:
        self.broadcaster_id: str = broadcaster_id
        self.id: str = id
        super().__init__()
    
class DeleteCustomRewardResponse(Utils.ResponseBaseClass):
    def __init__(self) -> None:
        super().__init__(None)

"""
Get Custom Reward
"""
class GetCustomRewardRequest(Utils.RequestBaseClass):
    requestType = Utils.HTTPMethod.GET
    scope = [Scope.Channel.Manage.Redemptions, Scope.Channel.Read.Redemptions]
    authorization = Utils.AuthRequired.USER
    endPoint ="/channel_points/custom_rewards"
    def __init__(self,broadcaster_id:str, id: Optional[str]=None, only_manageable_rewards: Optional[bool]=None) -> None:
        self.broadcaster_id = broadcaster_id
        self.id = id
        self.only_manageable_rewards = only_manageable_rewards
        super().__init__()

class GetCustomRewardResponse(Utils.ResponseBaseClass):
        def __init__(self) -> None:
            super().__init__(CustomRewardsItem)

"""
Get Custom Reward Redemption
"""
class GetCustomRewardRedemptionRequest(Utils.RequestBaseClass):
    requestType = Utils.HTTPMethod.GET
    scope = [Scope.Channel.Read.Redemptions, Scope.Channel.Manage.Redemptions]
    authorization = Utils.AuthRequired.USER
    endPoint ="/channel_points/custom_rewards/redemptions"
    def __init__(self, broadcaster_id: str, reward_id: Optional[str]=None,
                  status: Optional[str]=None, id: Optional[str]=None, 
                  sort: Optional[str]=None, after: Optional[str]=None, 
                  first:Optional[int]=None) -> None:
        self.broadcaster_id = broadcaster_id
        self.reward_id = reward_id
        self.status = status
        self.id = id
        self.sort = sort
        self.after = after 
        self.first = first
        super().__init__() 

class Reward:
        id: str
        title: str
        prompt: str
        cost: int
class CustomRewardRedemptionItem:
    broadcaster_name: str
    broadcaster_login: str
    broadcaster_id: str
    id: str
    user_id: str
    user_name: str
    user_input: str
    status:  str
    redeemed_at: str
    reward: Reward

class GetCustomRewardRedemptionResponse(Utils.ResponseBaseClass):
        def __init__(self) -> None:
            super().__init__(CustomRewardRedemptionItem)

"""
Update Custom Reward
"""
class UpdateCustomRewardRequest(Utils.RequestBaseClass):
    requestType = Utils.HTTPMethod.PATCH
    scope = Scope.Channel.Manage.Redemptions
    authorization = Utils.AuthRequired.USER
    endPoint ="/channel_points/custom_rewards"
    def __init__(self, broadcaster_id: str, 
                 id: str,
                 title: Optional[str]=None,
                 cost: Optional[int]=None,
                 prompt: Optional[str]=None,
                 is_enabled: Optional[bool]=None,
                 background_color: Optional[str]=None,
                 is_user_input_required: Optional[bool]=None,
                 is_max_per_stream_enabled: Optional[bool]=None,
                 max_per_stream: Optional[int]=None,
                 is_max_per_user_per_stream_enabled: Optional[bool]=None,
                 max_per_user_per_stream: Optional[int]=None,
                 is_global_cooldown_enabled: Optional[bool]=None,
                 global_cooldown_seconds: Optional[int]=None,
                 is_paused: Optional[bool]=None,
                 should_redemptions_skip_request_queue: Optional[bool]=None) -> None:    
        self.broadcaster_id = broadcaster_id
        self.id = id
        self.title = title
        self.cost = cost
        self.prompt = prompt
        self.is_enabled = is_enabled
        self.background_color = background_color
        self.is_user_input_required = is_user_input_required
        self.is_max_per_stream_enabled = is_max_per_stream_enabled
        self.max_per_stream = max_per_stream
        self.is_max_per_user_per_stream_enabled = is_max_per_user_per_stream_enabled
        self.max_per_user_per_stream = max_per_user_per_stream
        self.is_global_cooldown_enabled = is_global_cooldown_enabled
        self.global_cooldown_seconds = global_cooldown_seconds
        self.is_paused = is_paused
        self.should_redemptions_skip_request_queue = should_redemptions_skip_request_queue
        super().__init__()
    

class UpdateCustomRewardResponse(Utils.ResponseBaseClass):
        def __init__(self) -> None:
            super().__init__(CustomRewardsItem)

"""
Update Redemption Status
"""
class UpdateRedemptionStatusRequest(Utils.RequestBaseClass):
    requestType = Utils.HTTPMethod.PATCH
    scope = Scope.Channel.Manage.Redemptions
    authorization = Utils.AuthRequired.USER
    endPoint ="/channel_points/custom_rewards/redemptions"
    def __init__(self, id: str, broadcaster_id: str, reward_id: str, status: str ) -> None:
        self.id = id
        self.broadcaster_id = broadcaster_id
        self.reward_id = reward_id
        self.status = status
        super().__init__()
    

class UpdateRedemptionStatusResponse(Utils.ResponseBaseClass):
        def __init__(self) -> None:
            super().__init__(CustomRewardRedemptionItem)