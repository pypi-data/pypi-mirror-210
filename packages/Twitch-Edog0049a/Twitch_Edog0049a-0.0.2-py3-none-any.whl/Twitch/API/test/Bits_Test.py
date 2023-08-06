from ..Resources.Bits import BitsLeaderboardResponse, BitsLeaderboardItem
from .Utils import twitchAPICall
import unittest

class TestBitsLeaderboardResponse(unittest.TestCase):
    data = '''
    {
    "data": [
        {
        "user_id": "158010205",
        "user_login": "tundracowboy",
        "user_name": "TundraCowboy",
        "rank": 1,
        "score": 12543
        },
        {
        "user_id": "7168163",
        "user_login": "topramens",
        "user_name": "Topramens",
        "rank": 2,
        "score": 6900
        }
    ],
    "date_range": {
        "started_at": "2018-02-05T08:00:00Z",
        "ended_at": "2018-02-12T08:00:00Z"
    },
    "total": 2
    }
    '''
    response = BitsLeaderboardResponse()
    twitchAPICall(data, response)

    def test_data_type(self):
        self.assertIsInstance(self.response.data,list,"response data should be of type list")

    def test_data_listItem_type(self):
        self.assertIsInstance(self.response.data[0], BitsLeaderboardItem)
        self.assertIsInstance(self.response.data[1], BitsLeaderboardItem)

    def test_BitsLeaderboardItem_data(self):
        self.assertEqual(self.response.data[0].user_id, "158010205")
        self.assertEqual(self.response.data[0].user_login, "tundracowboy")
        self.assertEqual(self.response.data[0].user_name, "TundraCowboy")
        self.assertEqual(self.response.data[0].rank, 1)
        self.assertEqual(self.response.data[0].score, 12543)
if __name__ == '__main__':
    unittest.main()