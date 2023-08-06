import json
from ..Resources.Utils import ResponseBaseClass

def twitchAPICall( request:str, response:ResponseBaseClass) -> None:
        APIresponse:dict = json.loads(request)
        for key, value in APIresponse.items():
                response.__setattr__(key,value)