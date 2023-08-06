

from collections.abc import Iterable


class _Analytics:
    class _Read:
        
        @property 
        def Extensions(cls) -> str:
            """
            View analytics data for the Twitch Extensions owned by the authenticated account.\n              
            ---
            Required for:
                - Get Extension Analytics 
            """
            return "analytics:read:extensions"
        
        @property
        def Games(cls) -> str:
            """
            View analytics data for the games owned by the authenticated account.\n
            ---
            Required for:
                - Get Game Analytics
            """
            return "analytics:read:games"
    Read =_Read()
class _Bits:
    @property
    def Read(cls):
        """
        View Bits information for a channel.\n
        ---
        Required for:   
            - Get Bits Leaderboard
        """
        return"bits:read"

class _Channel:
    class _Edit:

        @property
        def Commercial(cls) -> str:
            """	
            Run commercials on a channel.\n
            ---
            Required for:
                - Start Commercial
            """
            return "channel:edit:commercial"
    
    class _Manage:

        @property
        def Broadcast(cls) -> str:
            """
            Manage a channel's broadcast configuration, including updating channel configuration 
            and managing stream markers and stream tags.\n
            ---
            Required for:
                - Modify Channel Information
                - Create Stream Marker
                - Replace Stream Tags     
            """
            return "channel:manage:broadcast"
        
        @property
        def Extensions(cls) -> str:
            """
            Manage a channel's Extension configuration, including activating Extensions.\n
            ---
            Required for:
                - Get User Active Extensions
                - Update User Extensions
            """
            return "channel:manage:extensions"
        
        @property
        def Moderators(cls) -> str:
            """
            Add or remove the moderator role from users in your channel.\n
            ---
            Required for:
                - Add Channel Moderator
                - Remove Channel Moderator        
            """
            return "channel:manage:moderators"
        
        @property
        def Polls(cls) -> str:
            """
            Manage a channel's polls.\n
            ---
            Required for:
                - Create Poll
                - End Poll 
            """
            return  "channel:manage:polls"

        @property
        def Predictions(cls) -> str:
            """
            Manage of channel's Channel Points Predictions\n
            ---
            Required for:
                - Create Channel Points Prediction
                - End Channel Points Prediction
            """
            return "channel:manage:predictions"

        @property
        def Raids(cls) -> str:
            """
            Manage a channel raiding another channel.\n
            ---
            Required for:
                - Start a raid
                - Cancel a raid
            """
            return "channel:manage:raids"
        
        @property
        def Redemptions(cls) -> str:
            """
            Manage Channel Points custom rewards and their redemptions on a channel.\n
            ---
            Required for:
                - Create Custom Rewards
                - Delete Custom Reward
                - Update Custom Reward
                - Update Redemption Status
            
            """
            return "channel:manage:redemptions"

        @property
        def Schedule(cls) -> str:
            """
            Manage a channel's stream schedule.\n
            ---
            Required for:
                - Update Channel Stream Schedule
                - Create Channel Stream Schedule Segment
                - Update Channel Stream Schedule Segment
                - Delete Channel Stream Schedule Segment
            
            """
            return "channel:manage:schedule"

        @property
        def Videos(cls) -> str:
            """
            Manage a channel's videos, including deleting videos.\n
            ---
            Required for:
                - Delete Videos
            """
            return "channel:manage:videos"
        
        @property
        def Vips(cls) -> str:
            """
            Add or remove the VIP role from users in your channel.\n
            ---
            Required for:
                - Get VIPs
                - Add Channel VIP
                - Remove Channel VIP
            
            """
            return "channel:manage:vips"
    
    class _Read:

        @property
        def Charity(cls) -> str:
            """
            Read charity campaign details and user donations on your channel.\n
            ---
            Required for:
                - Get Charity Campaign
            """
            return "channel:read:charity"
       
        @property
        def Editors(cls) -> str:
            """
            View a list of users with the editor role for a channel.\n
            ---
            Required for:
                - Get Channel Editors
            """
            return "channel:read:editors"

        @property
        def Goals(cls) -> str:
            """
            View Creator Goals for a channel.\n
            ---
            Required for:
                - Get Creator Goals
            """
            return "channel:read:goals"

        @property
        def Hype_train(cls) -> str:
            """
            View Hype Train information for a channel.\n
            ---
            Required for:
                - Get Hype Train Events            
            """
            return "channel:read:hype_train"

        @property
        def Polls(cls) -> str:
            return "channel:read:polls"
        
        @property
        def Predictions(cls) -> str:
            return "channel:read:predictions"
       
        @property
        def Redemptions(cls) -> str:
            return "channel:read:redemptions"

        @property
        def Stream_key(cls) -> str:
            return "channel:read:stream_key"

        @property
        def Subscriptions(cls) -> str:
            return "channel:read:subscriptions"

        @property
        def Vips(cls) -> str:
            return "channel:read:vips"
    Read = _Read()
    Manage = _Manage()
    Edit = _Edit()


class _Clips:

    @property
    def Edit(cls) -> str:
        return "clips:edit"

class _Moderation:

    @property
    def Read(cls) -> str:
        return "moderation:read"

class _Moderator:
    class _Manage:
        
        @property
        def Announcements(cls) -> str:
            return "moderator:manage:announcements"
        
        @property
        def Automod(cls) -> str:
            return "moderator:manage:automod"
        
        @property
        def Automod_settings(cls) -> str:
            return "moderator:manage:automod_settings"
        
        @property
        def Banned_users(cls) -> str:
            return "moderator:manage:banned_users"
        
        @property
        def Blocked_terms(cls) -> str:
            return "moderator:manage:blocked_terms"

        @property
        def Chat_messages(cls) -> str:
            return "moderator:manage:chat_messages"
        
        @property
        def Chat_settings(cls) -> str:
            return "moderator:manage:chat_settings"
        
        @property
        def Shield_mode(cls) -> str:
            return "moderator:manage:shield_mode"
        
        @property
        def Shoutouts(cls) -> str:
            return "moderator:manage:shoutouts"
        

    class _Read:
        
        @property
        def Automod_settings(cls) -> str:
            return "moderator:read:automod_settings"
        
        @property
        def Blocked_terms(cls) -> str:
            return "moderator:read:blocked_terms"
        
        @property
        def Chat_settings(cls) -> str:
            return "moderator:read:chat_settings"
                            
        @property
        def Chatters(cls)-> str:
            return "moderator:read:chatters"
            
        @property
        def Followers(cls) -> str:
            return "moderator:read:followers"
    
        @property
        def Shield_mode(cls) -> str:
            return "moderator:read:shield_mode"
        
        @property
        def Shoutouts(cls) -> str:
            return "moderator:read:shoutouts"
    Read = _Read()
    Manage = _Manage()

class _User:
    
    @property
    def Edit(cls) -> str:
        return "user:edit"
    
    class _Manage:

        @property
        def Blocked_users(cls) -> str:
            return "user:manage:blocked_users"
        
        @property
        def Chat_color(cls) -> str:
            return "user:manage:chat_color"
        
        @property
        def Whispers(cls) -> str:
            return "user:manage:whispers"
        
    class _Read:

        @property
        def Blocked_users(cls) -> str:
            return "user:read:blocked_users"
        
        @property
        def Broadcast(cls) -> str:
            return "user:read:broadcast"
        
        @property
        def Email(cls) -> str:
            return "user:read:email"
        
        @property
        def Follows(cls) -> str:
            return "user:read:follows"
        
        @property
        def Subscriptions(cls) -> str:
            return "user:read:subscriptions"
        
    Read = _Read()
    Manage = _Manage()


Analytics = _Analytics()
Bits = _Bits()
Clips = _Clips()
Channel = _Channel()
User = _User()
Moderation = _Moderation()
Moderator = _Moderator()
