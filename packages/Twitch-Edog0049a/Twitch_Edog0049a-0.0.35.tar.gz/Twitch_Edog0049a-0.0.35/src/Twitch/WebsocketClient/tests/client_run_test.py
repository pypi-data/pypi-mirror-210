import asyncio
import threading
import time
from typing import Optional
import unittest
import websockets
from ..WebsocketClient import WebsocketClient


def onconnect(sender,data):
    print(data)

class WebSocketTestServer:
    def __init__(self) -> None:
        self.__url: str = 'localhost'
        self.__port: int = 8088
        self.loop = asyncio.new_event_loop()
            
    async def _server(self):
        async with websockets.serve(self.msg_handler, self.__url, self.__port):
            print("server started")
            await asyncio.Future()
            
    async def msg_handler(self, websock, path):
        async for message in websock:
            print(f"server msg: {message}")
            await websock.send(message)

    def run(self, url:Optional[str]=None, port:Optional[int]=None):
        self.__url: str = url if url is not None else self.__url
        self.__port: int = port if port is not None else self.__port
        self.loop.create_task(self._server())
        self.loop.run_forever()
        
    def stop(self):
        if self.loop.is_running():
            self.loop.stop()

        
class websocketTestcase  (unittest.TestCase): 
    LastMessageSent = None
    lastMessageRecieved = None
    messageQ = []
    async def messageHandler(self, message):
         print(message)
         self.lastMessageRecieved=message

    async def sendmessage(self):
        if len(self.messageQ)>0:
            self.LastMessageSent = self.messageQ.pop()
            return self.LastMessageSent
        
    def setUp(self) -> None:
        print ("starting websocket echo test Server")
        self.wss = WebSocketTestServer()
        self.serverthread = threading.Thread(target=self.wss.run, name="WS_server", daemon=True).start()
        time.sleep(.01)
        print ("starting websocket Client")
        time.sleep(.01)
        self.websocketClient = WebsocketClient("ws://127.0.0.1:8088", self.messageHandler, self.sendmessage)
        self.websocketClient.events.on(self.websocketClient.EVENTENUM.CONNECTED,onconnect)
        self.clientThread = threading.Thread(target=self.websocketClient.connect, name="WS_client", daemon=True).start() 
        return super().setUp()
    
class testWebsocketClient1(websocketTestcase):
    def test_Send_Recieve(self):
        print("running test")
        self.messageQ.append("message")
        time.sleep(1)
        self.assertIsNotNone(self.LastMessageSent)
        self.assertIsNotNone(self.lastMessageRecieved)
        self.assertEqual(self.LastMessageSent,  self.lastMessageRecieved)

class testWebsocketClient2(unittest.TestCase):
    wait = True
    passed = False
    def setUp(self) -> None:
        print ("starting websocket Client")
        time.sleep(.01)
        self.websocketClient = WebsocketClient("ws://127.0.0.1:8088", self.messageHandler, self.sendmessage)
        self.clientThread = threading.Thread(target=self.websocketClient.connect, name="WS_client", daemon=True) 
        self.websocketClient.events.on(self.websocketClient.EVENTENUM.RECONNECTING,self.reconnectevent)
        return super().setUp()
    
    async def messageHandler(self, message):
         print(message)
         self.lastMessageRecieved=message

    async def sendmessage(self):
        if len(self.messageQ)>0:
            self.LastMessageSent = self.messageQ.pop()
            return self.LastMessageSent 
        
    def test_Reconnect(self):
        self.clientThread.start()
        while self.wait:
            time.sleep(.1)
        self.assertTrue(self.passed)

    def reconnectevent(self, sender, data):
        print("event recieved")
        print(self.websocketClient._reconnectTimer)
        if self.websocketClient._reconnectTimer > 16.00:
            self.websocketClient.stopReconnect()
            self.assertTrue(True)
            self.passed = True
            self.wait = False
            print("test ending")
        time.sleep(self.websocketClient._reconnectTimer)
            