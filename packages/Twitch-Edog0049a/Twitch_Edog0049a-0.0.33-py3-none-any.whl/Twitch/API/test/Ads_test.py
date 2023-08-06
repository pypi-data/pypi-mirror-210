from ..Resources.Ads import StartCommercialRepsonse
from .Utils import twitchAPICall
import unittest

class TestAdsReponse(unittest.TestCase):
    data ='''{
    "data": [
        {
        "length" : 60,
        "message" : "",
        "retry_after" : 480
        }
    ]
    }'''
    response = StartCommercialRepsonse()
    twitchAPICall(data, response)
    
    def test_response(self):
        self.assertEqual(self.response.data[0].length, 60)
        self.assertEqual(self.response.data[0].retry_after, 480)