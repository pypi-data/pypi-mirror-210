from aiohttp import ClientResponse, http_exceptions
from datetime import datetime
from typing import Callable, Optional
from Twitch.API.Exceptions import (
    TwitchApiBadRequstException, 
    TwitchApiNotFoundException, 
    TwitchApiTooManyRequestsException, 
    TwitchApiUnauthorizedException,
    TwitchApiInvalidRequestType,
    TwitchApiIvalidUserScope)
from Twitch.API.Resources.Utils import pagenation, dateRange, RequestBaseClass, ResponseBaseClass
from Twitch.API.Resources import *
from Twitch.API._ApiRequest import APIRequest
from Twitch.API.Resources import Utils

class Credentials:
    def __init__(self, id: str, OauthToken: str, scopes: list) -> None:
        self.id = id
        self.Oauth = OauthToken
        self.scopes = scopes
class twitchAPI:
    def __init__(self, clientCreds: Credentials, userCreds:Credentials) -> None:
        self.APIconnector = APIRequest("https://api.twitch.tv/helix")
        self._credentials:dict[Utils.AuthRequired, Credentials] = {
            Utils.AuthRequired.CLIENT: clientCreds,
            Utils.AuthRequired.USER : userCreds,
        }
        self._APIReqestFailedExcptions: dict = {
            Utils.HTTPStatus.BAD_REQUEST : TwitchApiBadRequstException,
            Utils.HTTPStatus.UNAUTHORIZED : TwitchApiUnauthorizedException,
            Utils.HTTPStatus.NOT_FOUND : TwitchApiNotFoundException,
            Utils.HTTPStatus.TOO_MANY_REQUESTS : TwitchApiTooManyRequestsException
        }
        self._ApiRequestSuccess: list= [
            Utils.HTTPStatus.OK,
            Utils.HTTPStatus.ACCEPTED,
            Utils.HTTPStatus.NO_CONTENT,
            Utils.HTTPStatus.CREATED,
        ]
    
    def _getParams(self, request: RequestBaseClass) -> list[tuple]:
        """
        turns request class variables into a list of tuples contains key/value pairs if variables are not None
        """
        params = list()
        for key, value in request.__dict__.items():
            if value is None:
                continue
            if isinstance(value, list):
                for item in value:
                    params.append((key, item))
            else:
                params.append((key,value))
        return params

    async def _twitchAPICall(self, request: RequestBaseClass, response: ResponseBaseClass, **kwargs) -> None:
        """
        Raises APIReqestFailedException(APIresponse)
        Raises TwitchApiIvalidUserScope
        """
        if request.authorization==Utils.AuthRequired.USER and request.scope is not None and request.scope not in self._credentials[Utils.AuthRequired.USER].scopes:
            raise TwitchApiIvalidUserScope("User doesn't have required scope!")    
        
        headers = {
            #set Authorization token based on api call required user 
            'Authorization': f'Bearer {self._credentials[request.authorization].Oauth}',
            'Client-Id': self._credentials[Utils.AuthRequired.CLIENT].id
        }

        APIresponse: ClientResponse = await self.APIconnector.request(request.endPoint, request.requestType, headers=headers, params=self._getParams(request))
        if APIresponse.status in self._ApiRequestSuccess:
            response.raw = await APIresponse.json()
            response.status = APIresponse.status
            for key, value in response.raw.items():
                    response.__setattr__(key, value)
            return
        raise self._APIReqestFailedExcptions[APIresponse.status](await APIresponse.json())

    async def StartCommercial(self, length: int) -> StartCommercialRepsonse:
        request = StartCommercialRequest(self._credentials[Utils.UserType.BROADCASTER].id, length)
        response = StartCommercialRepsonse()
        await self._twitchAPICall(request, response)
        return response

    async def GetExtensionAnalytics(self,extension_id: Optional[str]= None, 
                type: Optional[str]= None,
                started_at: Optional[datetime] = None,
                ended_at: Optional[datetime] = None,
                first: Optional[int] = None,
                after: Optional[str] = None) -> GetExtensionAnalyticsResponse:
         
        request = GetExtensionAnalyticsRequest(extension_id, type, started_at, ended_at, first, after)       
        response = GetExtensionAnalyticsResponse()
        await self._twitchAPICall(request, response)
        return response
    
    async def GetGameAnalytics(self,                 
                 game_id: Optional[str] = None,
                 type: Optional[str]= None,
                 started_at: Optional[datetime] = None,
                 ended_at: Optional[datetime] = None,
                 first: Optional[int] = None,
                 after: Optional[str] = None ) -> GetGameAnalyticsResponse:
        
        request = GetGameAnalyticsRequest(game_id, type, started_at, ended_at, first, after)
        response = GetGameAnalyticsResponse()
        await self._twitchAPICall(request, response)
        return response

    async def GetBitsLeaderboard(self, count:Optional[int]=None, 
                                 period: Optional[str]=None, 
                                 started_at: Optional[datetime]=None, 
                                 user_id: Optional[str]=None) -> GetBitsLeaderboardResponse:
        request = GetBitsLeaderboardRequest(count, period, started_at, user_id)
        response = GetBitsLeaderboardResponse()
        await self._twitchAPICall(request, response)
        return response

    async def GetCheermotes(self, broadcaster_id: Optional[str] = None) -> GetCheermotesResponse:
        request = GetCheermotesRequest(broadcaster_id)
        response = GetCheermotesResponse()
        await self._twitchAPICall(request, response)
        return response

    async def GetExtensionTransactions(self, extension_id:str, 
                                       id: Optional[str]=None, 
                                       first: Optional[int]=None, 
                                       after: Optional[str]=None) -> GetExtensionTransactionsResponse:
        request = GetExtensionTransactionsRequest(extension_id, id, first, after)
        response = GetExtensionTransactionsResponse()
        await self._twitchAPICall(request, response)
        return response

    async def GetChannelInformation(self, broadcaster_ids:list, userAuth=False) -> GetChannelInformationResponse:
        request = GetChannelInformationRequest(broadcaster_ids, userAuth)
        response = GetChannelInformationResponse()
        await self._twitchAPICall(request, response)
        return response

    async def ModifyChannelInformation(self, title:Optional[str]=None, 
                                       delay:Optional[int]=None, 
                                       tags:Optional[list[str]]=None) -> ModifyChannelInformationResponse:
        request = ModifyChannelInformationRequest(self._credentials[Utils.AuthRequired.USER].id, title, delay, tags)
        response = GetExtensionTransactionsResponse()
        await self._twitchAPICall(request, response)
        return response
        
    async def GetChannelEditors(self) -> GetChannelEditorsResponse:
        request = GetChannelEditorsRequest(self._credentials[Utils.AuthRequired.USER].id)
        response = GetChannelEditorsResponse()
        await self._twitchAPICall(request, response)
        return response
    
    async def GetFollowedChannels(self, broadcaster_id: Optional[str]=None, 
                                  first:Optional[int]=None, 
                                  after: Optional[str]=None) -> GetFollowedChannelsResponse:
        request = GetFollowedChannelsRequest(self._credentials[Utils.AuthRequired.USER].id, broadcaster_id, first, after)
        response = GetFollowedChannelsResponse()
        await self._twitchAPICall(request, response)
        return response

    async def CreateCustomRewards(self, title: str, 
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
                                should_redemptions_skip_request_queue: Optional[bool]=None) -> CreateCustomRewardsResponse:
        
        request = CreateCustomRewardsRequest(self._credentials[Utils.AuthRequired.USER].id, 
                                             title, cost, 
                                             prompt, is_enabled, 
                                             background_color, is_user_input_required,
                                             is_max_per_stream_enabled, max_per_stream,
                                             is_max_per_user_per_stream_enabled, 
                                             max_per_user_per_stream,
                                             is_global_cooldown_enabled,
                                             global_cooldown_seconds,
                                             should_redemptions_skip_request_queue)
        
        response = CreateCustomRewardsResponse()
        await self._twitchAPICall(request, response)
        return response
    
    async def DeleteCustomReward(self, id: str) -> DeleteCustomRewardResponse:
        request = DeleteCustomRewardRequest(self._credentials[Utils.AuthRequired.USER].id, id)
        response = DeleteCustomRewardResponse()
        await self._twitchAPICall(request, response)
        return response
    
    async def GetCustomReward(self) -> GetCustomRewardResponse:
        request = GetCustomRewardRequest()
        response = GetCustomRewardResponse()
        await self._twitchAPICall(request, response)
        return response
    
    async def GetCustomRewardRedemption(self) -> GetCustomRewardRedemptionResponse:
        request = GetCustomRewardRedemptionRequest()
        response = GetCustomRewardRedemptionResponse()
        await self._twitchAPICall(request, response)
        return response
    
    async def UpdateCustomReward(self) -> UpdateCustomRewardResponse:
        request = UpdateCustomRewardRequest()
        response = UpdateCustomRewardResponse()
        await self._twitchAPICall(request, response)
        return response

    async def UpdateRedemptionStatus(self) -> UpdateRedemptionStatusResponse:
        request = UpdateRedemptionStatusRequest()
        response = UpdateRedemptionStatusResponse()
        await self._twitchAPICall(request, response)
        return response
    
    async def GetCharityCampaign(self) -> GetCharityCampaignResponse:
        request = GetCharityCampaignRequest()
        response = GetCharityCampaignResponse()
        await self._twitchAPICall(request, response)
        return response
    
    async def GetCharityCampaignDonations(self) -> GetCharityCampaignDonationsResponse:
        request = GetCharityCampaignDonationsRequest()
        response = GetCharityCampaignDonationsResponse()
        await self._twitchAPICall(request, response)
        return response
    
    async def GetChatters(self) -> GetChattersResponse:
        request = GetChattersRequest()
        response = GetChattersResponse()
        await self._twitchAPICall(request, response)
        return response
    
    async def GetChannelEmotes(self) -> GetChannelEmotesResponse:
        request = GetChannelEmotesRequest()
        response = GetChannelEmotesResponse()
        await self._twitchAPICall(request, response)
        return response
    
    async def GetGlobalEmotes(self) -> GetGlobalEmotesResponse:
        request = GetGlobalEmotesRequest()
        response = GetGlobalEmotesResponse()
        await self._twitchAPICall(request, response)
        return response
    
    async def GetEmoteSets(self) -> GetEmoteSetsResponse:
        request = GetEmoteSetsRequest()
        response = GetEmoteSetsResponse()
        await self._twitchAPICall(request, response)
        return response
    
    async def GetChannelChatBadges(self) -> GetChannelChatBadgesResponse:
        request = GetChannelChatBadgesRequest()
        response = GetChannelChatBadgesResponse()
        await self._twitchAPICall(request, response)
        return response
    
    async def GetGlobalChatBadges(self) -> GetGlobalChatBadgesResponse:
        request = GetGlobalChatBadgesRequest()
        response = GetGlobalChatBadgesResponse()
        await self._twitchAPICall(request, response)
        return response
    
    async def GetChatSettings(self) -> GetChatSettingsResponse:
        request = GetChatSettingsRequest()
        response = GetChatSettingsResponse()
        await self._twitchAPICall(request, response)
        return response
    
    async def UpdateChatSettings(self) -> UpdateChatSettingsResponse:
        request = UpdateChatSettingsRequest()
        response = UpdateChatSettingsResponse()
        await self._twitchAPICall(request, response)
        return response
    
    async def SendChatAnnouncement(self) -> SendChatAnnouncementResponse:
        request = SendChatAnnouncementRequest()
        response = SendChatAnnouncementResponse()
        await self._twitchAPICall(request, response)
        return response
    
    async def SendaShoutout(self) -> SendaShoutoutResponse:
        request = SendaShoutoutRequest()
        response = SendaShoutoutResponse()
        await self._twitchAPICall(request, response)
        return response
    
    async def GetUserChatColor(self) -> GetUserChatColorResponse:
        request = GetUserChatColorRequest()
        response = GetUserChatColorResponse()
        await self._twitchAPICall(request, response)
        return response
    
    async def UpdateUserChatColor(self) -> UpdateUserChatColorResponse:
        request = UpdateUserChatColorRequest()
        response = UpdateUserChatColorResponse()
        await self._twitchAPICall(request, response)
        return response
    
    async def CreateClip(self) -> CreateClipResponse:
        request = CreateClipRequest()
        response = CreateClipResponse()
        await self._twitchAPICall(request, response)
        return response
    
    async def GetClips(self) -> GetClipsResponse:
        request = GetClipsRequest()
        response = GetClipsResponse()
        await self._twitchAPICall(request, response)
        return response
    
    async def GetDropsEntitlements(self) -> GetDropsEntitlementsResponse:
        request = GetDropsEntitlementsRequest()
        response = GetDropsEntitlementsResponse()
        await self._twitchAPICall(request, response)
        return response
    
    async def UpdateDropsEntitlements(self) -> UpdateDropsEntitlementsResponse:
        request = UpdateDropsEntitlementsRequest()
        response = UpdateDropsEntitlementsResponse()
        await self._twitchAPICall(request, response)
        return response
    
    async def GetExtensionConfigurationSegment(self) -> GetExtensionConfigurationSegmentResponse:
        request = GetExtensionConfigurationSegmentRequest()
        response = GetExtensionConfigurationSegmentResponse()
        await self._twitchAPICall(request, response)
        return response
    
    async def SetExtensionConfigurationSegment(self) -> SetExtensionConfigurationSegmentResponse:
        request = SetExtensionConfigurationSegmentRequest()
        response = SetExtensionConfigurationSegmentResponse()
        await self._twitchAPICall(request, response)
        return response
    
    async def SetExtensionRequiredConfiguration(self) -> SetExtensionRequiredConfigurationResponse:
        request = SetExtensionRequiredConfigurationRequest()
        response = SetExtensionRequiredConfigurationResponse()
        await self._twitchAPICall(request, response)
        return response
    
    async def SendExtensionPubSubMessage(self) -> SendExtensionPubSubMessageResponse:
        request = SendExtensionPubSubMessageRequest()
        response = SendExtensionPubSubMessageResponse()
        await self._twitchAPICall(request, response)
        return response
    
    async def GetExtensionLiveChannels(self) -> GetExtensionLiveChannelsResponse:
        request = GetExtensionLiveChannelsRequest()
        response = GetExtensionLiveChannelsResponse()
        await self._twitchAPICall(request, response)
        return response
    
    async def GetExtensionSecrets(self) -> GetExtensionSecretsResponse:
        request = GetExtensionSecretsRequest()
        response = GetExtensionSecretsResponse()
        await self._twitchAPICall(request, response)
        return response
    
    async def CreateExtensionSecret(self) -> CreateExtensionSecretResponse:
        request = CreateExtensionSecretRequest()
        response = CreateExtensionSecretResponse()
        await self._twitchAPICall(request, response)
        return response
    
    async def SendExtensionChatMessage(self) -> SendExtensionChatMessageResponse:
        request = SendExtensionChatMessageRequest()
        response = SendExtensionChatMessageResponse()
        await self._twitchAPICall(request, response)
        return response
    
    async def GetExtensions(self) -> GetExtensionsResponse:
        request = GetExtensionsRequest()
        response = GetExtensionsResponse()
        await self._twitchAPICall(request, response)
        return response

    async def GetReleasedExtensions(self) -> GetReleasedExtensionsResponse:
        request = GetReleasedExtensionsRequest()
        response = GetReleasedExtensionsResponse()
        await self._twitchAPICall(request, response)
        return response

    async def GetExtensionBitsProducts(self) -> GetExtensionBitsProductsResponse:
        request = GetExtensionBitsProductsRequest()
        response = GetExtensionBitsProductsResponse()
        await self._twitchAPICall(request, response)
        return response
    
    async def UpdateExtensionBitsProduct(self) -> UpdateExtensionBitsProductResponse:
        request = UpdateExtensionBitsProductRequest()
        response = UpdateExtensionBitsProductResponse()
        await self._twitchAPICall(request, response)
        return response
    
    async def CreateEventSubSubscription(self) -> CreateEventSubSubscriptionResponse:
        request = CreateEventSubSubscriptionRequest()
        response = CreateEventSubSubscriptionResponse()
        await self._twitchAPICall(request, response)
        return response
    
    async def DeleteEventSubSubscription(self) -> DeleteEventSubSubscriptionResponse:
        request = DeleteEventSubSubscriptionRequest()
        response = DeleteEventSubSubscriptionResponse()
        await self._twitchAPICall(request, response)
        return response
    
    async def GetEventSubSubscriptions(self) -> GetEventSubSubscriptionsResponse:
        request = GetEventSubSubscriptionsRequest()
        response = GetEventSubSubscriptionsResponse()
        await self._twitchAPICall(request, response)
        return response

    async def GetTopGames(self) -> GetTopGamesResponse:
        request = GetTopGamesRequest()
        response = GetTopGamesResponse()
        await self._twitchAPICall(request, response)
        return response
    
    async def GetGames(self) -> GetGamesResponse:
        request = GetGamesRequest()
        response = GetGamesResponse()
        await self._twitchAPICall(request, response)
        return response
    
    async def GetCreatorGoals(self) -> GetCreatorGoalsResponse:
        request = GetCreatorGoalsRequest()
        response = GetCreatorGoalsResponse()
        await self._twitchAPICall(request, response)
        return response
    
    async def GetHypeTrainEvents(self) -> GetHypeTrainEventsResponse:
        request = GetHypeTrainEventsRequest()
        response = GetHypeTrainEventsResponse()
        await self._twitchAPICall(request, response)
        return response
    
    async def CheckAutoModStatus(self) -> CheckAutoModStatusResponse:
        request = CheckAutoModStatusRequest()
        response = CheckAutoModStatusResponse()
        await self._twitchAPICall(request, response)
        return response
    
    async def ManageHeldAutoModMessages(self) -> ManageHeldAutoModMessagesResponse:
        request = ManageHeldAutoModMessagesRequest()
        response = ManageHeldAutoModMessagesResponse()
        await self._twitchAPICall(request, response)
        return response
    
    async def GetAutoModSettings(self) -> GetAutoModSettingsResponse:
        request = GetAutoModSettingsRequest()
        response = GetAutoModSettingsResponse()
        await self._twitchAPICall(request, response)
        return response
    
    async def UpdateAutoModSettings(self) -> UpdateAutoModSettingsResponse:
        request = UpdateAutoModSettingsRequest()
        response = UpdateAutoModSettingsResponse()
        await self._twitchAPICall(request, response)
        return response
    
    async def GetBannedUsers(self) -> GetBannedUsersResponse:
        request = GetBannedUsersRequest()
        response = GetBannedUsersResponse()
        await self._twitchAPICall(request, response)
        return response
    
    async def BanUser(self) -> BanUserResponse:
        request = BanUserRequest()
        response = BanUserResponse()
        await self._twitchAPICall(request, response)
        return response
    
    async def UnbanUser(self) -> UnbanUserResponse:
        request = UnbanUserRequest()
        response = UnbanUserResponse()
        await self._twitchAPICall(request, response)
        return response
    
    async def GetBlockedTerms(self) -> GetBlockedTermsResponse:
        request = GetBlockedTermsRequest()
        response = GetBlockedTermsResponse()
        await self._twitchAPICall(request, response)
        return response
    
    async def AddBlockedTerm(self) -> AddBlockedTermResponse:
        request = AddBlockedTermRequest()
        response = AddBlockedTermResponse()
        await self._twitchAPICall(request, response)
        return response
    
    async def RemoveBlockedTerm(self) -> RemoveBlockedTermResponse:
        request = RemoveBlockedTermRequest()
        response = RemoveBlockedTermResponse()
        await self._twitchAPICall(request, response)
        return response

    async def DeleteChatMessages(self) -> DeleteChatMessagesResponse:
        request = DeleteChatMessagesRequest()
        response = DeleteChatMessagesResponse()
        await self._twitchAPICall(request, response)
        return response
    
    async def GetModerators(self) -> GetModeratorsResponse:
        request = GetModeratorsRequest()
        response = GetModeratorsResponse()
        await self._twitchAPICall(request, response)
        return response
    
    async def AddChannelModerator(self) -> AddChannelModeratorResponse:
        request = AddChannelModeratorRequest()
        response = AddChannelModeratorResponse()
        await self._twitchAPICall(request, response)
        return response
    
    async def RemoveChannelModerator(self) -> RemoveChannelModeratorResponse:
        request = RemoveChannelModeratorRequest()
        response = RemoveChannelModeratorResponse()
        await self._twitchAPICall(request, response)
        return response
    
    async def GetVIPs(self) -> GetVIPsResponse:
        request = GetVIPsRequest()
        response = GetVIPsResponse()
        await self._twitchAPICall(request, response)
        return response
    
    async def AddChannelVIP(self) -> AddChannelVIPResponse:
        request = AddChannelVIPRequest()
        response = AddChannelVIPResponse()
        await self._twitchAPICall(request, response)
        return response
    
    async def RemoveChannelVIP(self) -> RemoveChannelVIPResponse:
        request = RemoveChannelVIPRequest()
        response = RemoveChannelVIPResponse()
        await self._twitchAPICall(request, response)
        return response
    
    async def UpdateShieldModeStatus(self) -> UpdateShieldModeStatusResponse:
        request = UpdateShieldModeStatusRequest()
        response = UpdateShieldModeStatusResponse()
        await self._twitchAPICall(request, response)
        return response
    
    async def GetShieldModeStatus(self) -> GetShieldModeStatusResponse:
        request = GetShieldModeStatusRequest()
        response = GetShieldModeStatusResponse()
        await self._twitchAPICall(request, response)
        return response
    
    async def GetPolls(self) -> GetPollsResponse:
        request = GetPollsRequest()
        response = GetPollsResponse()
        await self._twitchAPICall(request, response)
        return response
    
    async def CreatePoll(self) -> CreatePollResponse:
        request = CreatePollRequest()
        response = CreatePollResponse()
        await self._twitchAPICall(request, response)
        return response
    
    async def EndPoll(self) -> EndPollResponse:
        request = EndPollRequest()
        response = EndPollResponse()
        await self._twitchAPICall(request, response)
        return response
    
    async def GetPredictions(self) -> GetPredictionsResponse:
        request = GetPredictionsRequest()
        response = GetPredictionsResponse()
        await self._twitchAPICall(request, response)
        return response
    
    async def CreatePrediction(self) -> CreatePredictionResponse:
        request = CreatePredictionRequest()
        response = CreatePredictionResponse()
        await self._twitchAPICall(request, response)
        return response
    
    async def EndPrediction(self) -> EndPredictionResponse:
        request = EndPredictionRequest()
        response = EndPredictionResponse()
        await self._twitchAPICall(request, response)
        return response
    
    async def Startaraid(self) -> StartaraidResponse:
        request = StartaraidRequest()
        response = StartaraidResponse()
        await self._twitchAPICall(request, response)
        return response
    
    async def Cancelaraid(self) -> CancelaraidResponse:
        request = CancelaraidRequest()
        response = CancelaraidResponse()
        await self._twitchAPICall(request, response)
        return response
    
    async def GetChannelStreamSchedule(self) -> GetChannelStreamScheduleResponse:
        request = GetChannelStreamScheduleRequest()
        response = GetChannelStreamScheduleResponse()
        await self._twitchAPICall(request, response)
        return response
    
    async def GetChanneliCalendar(self) -> GetChanneliCalendarResponse:
        request = GetChanneliCalendarRequest()
        response = GetChanneliCalendarResponse()
        await self._twitchAPICall(request, response)
        return response
    
    async def UpdateChannelStreamSchedule(self) -> UpdateChannelStreamScheduleResponse:
        request = UpdateChannelStreamScheduleRequest()
        response = UpdateChannelStreamScheduleResponse()
        await self._twitchAPICall(request, response)
        return response
    
    async def CreateChannelStreamScheduleSegment(self) -> CreateChannelStreamScheduleSegmentResponse:
        request = CreateChannelStreamScheduleSegmentRequest()
        response = CreateChannelStreamScheduleSegmentResponse()
        await self._twitchAPICall(request, response)
        return response
    
    async def UpdateChannelStreamScheduleSegment(self) -> UpdateChannelStreamScheduleSegmentResponse:
        request = UpdateChannelStreamScheduleSegmentRequest()
        response = UpdateChannelStreamScheduleSegmentResponse()
        await self._twitchAPICall(request, response)
        return response
    
    async def DeleteChannelStreamScheduleSegment(self) -> DeleteChannelStreamScheduleSegmentResponse:
        request = DeleteChannelStreamScheduleSegmentRequest()
        response = DeleteChannelStreamScheduleSegmentResponse()
        await self._twitchAPICall(request, response)
        return response
    
    async def SearchCategories(self) -> SearchCategoriesResponse:
        request = SearchCategoriesRequest()
        response = SearchCategoriesResponse()
        await self._twitchAPICall(request, response)
        return response
    
    async def SearchChannels(self) -> SearchChannelsResponse:
        request = SearchChannelsRequest()
        response = SearchChannelsResponse()
        await self._twitchAPICall(request, response)
        return response
    
    async def GetSoundtrackCurrentTrack(self) -> GetSoundtrackCurrentTrackResponse:
        request = GetSoundtrackCurrentTrackRequest()
        response = GetSoundtrackCurrentTrackResponse()
        await self._twitchAPICall(request, response)
        return response
    
    async def GetSoundtrackPlaylist(self) -> GetSoundtrackPlaylistResponse:
        request = GetSoundtrackPlaylistRequest()
        response = GetSoundtrackPlaylistResponse()
        await self._twitchAPICall(request, response)
        return response
    
    async def GetSoundtrackPlaylists(self) -> GetSoundtrackPlaylistsResponse:
        request = GetSoundtrackPlaylistsRequest()
        response = GetSoundtrackPlaylistsResponse()
        await self._twitchAPICall(request, response)
        return response
    
    async def GetStreamKey(self) -> GetStreamKeyResponse:
        request = GetStreamKeyRequest()
        response = GetStreamKeyResponse()
        await self._twitchAPICall(request, response)
        return response
    
    async def GetStreams(self) -> GetStreamsResponse:
        request = GetStreamsRequest()
        response = GetStreamsResponse()
        await self._twitchAPICall(request, response)
        return response
    
    async def GetFollowedStreams(self) -> GetFollowedStreamsResponse:
        request = GetFollowedStreamsRequest()
        response = GetFollowedStreamsResponse()
        await self._twitchAPICall(request, response)
        return response
    
    async def CreateStreamMarker(self) -> CreateStreamMarkerResponse:
        request = CreateStreamMarkerRequest()
        response = CreateStreamMarkerResponse()
        await self._twitchAPICall(request, response)
        return response
    
    async def GetStreamMarkers(self) -> GetStreamMarkersResponse:
        request = GetStreamMarkersRequest()
        response = GetStreamMarkersResponse()
        await self._twitchAPICall(request, response)
        return response
    
    async def GetBroadcasterSubscriptions(self) -> GetBroadcasterSubscriptionsResponse:
        request = GetBroadcasterSubscriptionsRequest()
        response = GetBroadcasterSubscriptionsResponse()
        await self._twitchAPICall(request, response)
        return response
    
    async def CheckUserSubscription(self) -> CheckUserSubscriptionResponse:
        request = CheckUserSubscriptionRequest()
        response = CheckUserSubscriptionResponse()
        await self._twitchAPICall(request, response)
        return response

    async def GetAllStreamTags(self) -> GetAllStreamTagsResponse:
        request = GetAllStreamTagsRequest()
        response = GetAllStreamTagsResponse()
        await self._twitchAPICall(request, response)
        return response
    
    async def GetStreamTags(self) -> GetStreamTagsResponse:
        request = GetStreamTagsRequest()
        response = GetStreamTagsResponse()
        await self._twitchAPICall(request, response)
        return response
    
    async def GetChannelTeams(self) -> GetChannelTeamsResponse:
        request = GetChannelTeamsRequest()
        response = GetChannelTeamsResponse()
        await self._twitchAPICall(request, response)
        return response

    async def GetTeams(self) -> GetTeamsResponse:
        request = GetTeamsRequest()
        response = GetTeamsResponse()
        await self._twitchAPICall(request, response)
        return response
    
    async def GetUsers(self,id:Optional[str]=None, login: Optional[str]=None) -> GetUsersResponse:
        request = GetUsersRequest(id=id, login=login)
        response = GetUsersResponse()
        await self._twitchAPICall(request, response)
        return response
    
    async def UpdateUser(self) -> UpdateUserResponse:
        request = UpdateUserRequest()
        response = UpdateUserResponse()
        await self._twitchAPICall(request, response)
        return response

    async def GetUserBlockList(self) -> GetUserBlockListResponse:
        request = GetUserBlockListRequest()
        response = GetUserBlockListResponse()
        await self._twitchAPICall(request, response)
        return response
    
    async def BlockUser(self) -> BlockUserResponse:
        request = BlockUserRequest()
        response = BlockUserResponse()
        await self._twitchAPICall(request, response)
        return response
    
    async def UnblockUser(self) -> UnblockUserResponse:
        request = UnblockUserRequest()
        response = UnblockUserResponse()
        await self._twitchAPICall(request, response)
        return response
    
    async def GetUserExtensions(self) -> GetUserExtensionsResponse:
        request = GetUserExtensionsRequest()
        response = GetUserExtensionsResponse()
        await self._twitchAPICall(request, response)
        return response

    async def GetUserActiveExtensions(self) -> GetUserActiveExtensionsResponse:
        request = GetUserActiveExtensionsRequest()
        response = GetUserActiveExtensionsResponse()
        await self._twitchAPICall(request, response)
        return response
    
    async def UpdateUserExtensions(self) -> UpdateUserExtensionsResponse:
        request = UpdateUserExtensionsRequest()
        response = UpdateUserExtensionsResponse()
        await self._twitchAPICall(request, response)
        return response

    async def GetVideos(self, id: Optional[str]=None, user_id: Optional[str]=None, 
            game_id: Optional[str]=None, language: Optional[str]=None, 
            period: Optional[str]=None, sort: Optional[str]=None, 
            type: Optional[str]=None, first: Optional[str]=None, 
            after: Optional[str]=None, before: Optional[str]=None) -> GetVideosResponse:
        request = GetVideosRequest()
        response = GetVideosResponse()
        await self._twitchAPICall(request, response)
        return response

    async def DeleteVideos(self, id: str | list ) -> DeleteVideosResponse:
        request = DeleteVideosRequest(id)
        response = DeleteVideosResponse()
        await self._twitchAPICall(request, response)
        return response

    async def SendWhisper(self, to_user_id: str, message: str) -> SendWhisperResponse:
        request = SendWhisperRequest(self._credentials[SendWhisperRequest.authorization].id, to_user_id, message)
        response = SendWhisperResponse()
        await self._twitchAPICall(request, response)
        return response