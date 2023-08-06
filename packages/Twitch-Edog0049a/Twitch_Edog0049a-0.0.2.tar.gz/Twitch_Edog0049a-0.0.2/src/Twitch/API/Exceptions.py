class TwitchApiUnauthorizedException(Exception):
     pass
class TwitchApiBadRequstException(Exception):
     pass
class TwitchApiNotFoundException(Exception):
     pass
class TwitchApiTooManyRequestsException(Exception):
     pass

class TwitchApiInvalidRequestType(Exception):
     pass

class TwitchApiIvalidUserScope(Exception):
     pass