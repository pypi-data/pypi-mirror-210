class _Channel:
    @property
    def Update(cls):
        return "channel.update"
    
    @property
    def Follow(cls):
        return "channel.follow"
    
    @property
    def Subscribe(cls):
        return "channel.subscribe"
    
    class _Subscription:
        @property
        def End(cls):
            return "channel.subscription.end"
        
        @property
        def Gift(cls):
            return "channel.subscription.gift"
        
        def Message(cls):
            return "channel.subscription.message"
        
    @property
    def Cheer(cls):
        return "channel.cheer"
    
    @property
    def Raid(cls):
        return "channel.raid"
    
    @property
    def Ban(cls):
        return "channel.ban"
    
    @property
    def Unban(cls):
        return "channel.unban"
    
    class _Moderator:
        @property
        def Add(cls):
            return "channel.moderator.add"

        @property
        def Remove(cls):
            return "channel.moderator.remove"

    class _GuestStarSession:
        @property
        def Begin(cls):
            return "channel.guest_star_session.begin"
        
        @property
        def End(cls):
            return "channel.guest_star_session.end"
    
    class _GuestStarGuest:
        @property
        def Update(cls):
            return "channel.guest_star_guest.update"
        
    class _GuestStarSlot:   
        @property
        def Update(cls):
            return "channel.guest_star_slot.update"
        
    class _GuestStarSettings:  
        @property
        def Update(cls):
            return "channel.guest_star_settings.update"



    Subscription = _Subscription()
    Moderator = _Moderator()
    GuestStarSession = _GuestStarSession()
    GuestStarGuest = _GuestStarGuest()
    GuestStarSlot = _GuestStarSlot()
    GuestStarSettings = _GuestStarSettings()



Channel = _Channel()