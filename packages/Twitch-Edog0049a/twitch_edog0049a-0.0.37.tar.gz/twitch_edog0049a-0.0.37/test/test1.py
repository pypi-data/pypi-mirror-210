from typing import Callable
import Twitch
import time
import unittest
from Twitch.secretkeys import apikeys
def message(sender, msg):
    print (msg)
class chat_con(unittest.TestCase):
    def setUp(self) -> None:
        settings={
        "server": "irc.chat.twitch.tv",
        "port": 6667,
        "user": "edog0049a",
        "password":f"oauth:{apikeys.BOT_OAUTH}",
        "channels": ["alilfoxz","edog0049a"],
        "caprequest" :"twitch.tv/tags twitch.tv/commands twitch.tv/membership" 
        }
        self.chat = Twitch.ChatInerface(settings)
        self.chat.onConnected(message)
        self.chat.onReceived(message)
        
        self.chat.run()

        return super().setUp()
    def tearDown(self) -> None:
        self.chat.disconnect()
        return super().tearDown()
    
    def test(self):
        M = 0
        print(isinstance(message, Callable))
        print(isinstance(M, Callable))
        self.chat.connect()
        time.sleep(5)