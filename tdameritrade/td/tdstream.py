"""
    Copyright (C) 2018 Matthew LeMieux
    
    This file is part of a third party TDAmeritrade API Library, called MLTDAmeritrade.

    MLTDAmeritrade is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    MLTDAmeritrade is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with MLTDAmeritrade.  If not, see <http://www.gnu.org/licenses/>.
"""

import tdameritrade.td.tdhelper as tdhelper
import urllib
import json
import websocket
from threading import Thread
import time
import os

class TDStream(object):
    streamInfo = None
    loggedIn = False
    requestCounter = 0
    isClosed = False
    
    def __init__(self):
        pass
    
    def on_message(self, ws, message):
        print(message)
        if True:
            self.loggedIn = True
        print("received_message")
        
    def on_cont_message(self, ws, message):
        print(message)
        if True:
            self.loggedIn = True
        print("received_message")
        
    def on_data(self, ws, data, a, b):
        print(data)
        print("received_data")
    
    
    def on_error(self, ws, error):
        print(error)
    
    
    def on_close(self, ws):
        self.isClosed = True
        # setTimeout(setupWebSocket, 1000);
        print("### closed ###")
    
    
    def on_open(self, ws):
        def run(*args):
            loginMessage = self.loginMessage(self.streamInfo)
            try:
                ws.send(loginMessage)
                # send the message, then wait
                # so thread doesn't exit and socket
                # isn't closed
                while not self.loggedIn and not self.isClosed:
                    time.sleep(1)
            except Exception as e:
                print(str(e))
                print(os.sys.exc_info()[0:2])
                print("end exception")
            
            #ws.close()
            print("Thread terminating...")
    
        try: 
            Thread(target=run).start()
        except Exception as e:
            print(str(e))
            print(os.sys.exc_info()[0:2])
            print("end exception")

    def start(self):
        tdh = tdhelper.TDHelper()
        am = tdhelper.AuthManager()
        authData = am.get_token()
        self.streamInfo = tdh.getStreamerInfo()
        host = "wss://"+self.streamInfo['streamerInfo']['streamerSocketUrl']+"/ws"
        websocket.enableTrace(True)
        authValue = authData['token_type'] + ' ' + authData['access_token']
        ws = websocket.WebSocketApp(
            host, on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close, 
            on_data=self.on_data,
            on_cont_message=self.on_cont_message, 
            header = ['Authorization: '+authValue]
            )
        ws.on_open = self.on_open
        try:
            ws.run_forever()
        except Exception as e:
            print(e)
            print(os.sys.exc_info()[0:2])
            print("done reporting exception") 


    def requestId(self):
        ret = self.requestCounter
        self.requestCounter += 1
        return(ret)
        
    def chart_history(self):
        pass

    def loginMessage(self, streamInfo):
        credential = {
            'acl': streamInfo['streamerInfo']['acl'],
            'token': streamInfo['streamerInfo']['token'],
            'appid': streamInfo['streamerInfo']['appId'],
            'userid': streamInfo['accounts'][0]['accountId'],
            'company': streamInfo['accounts'][0]['company'],
            'segment': streamInfo['accounts'][0]['segment'],
            'cddomain': streamInfo['accounts'][0]['accountCdDomainId'],
            'timestamp': int(round(time.time() * 1000)),
            'usergroup': streamInfo['streamerInfo']['userGroup'],
            'accesslevel': streamInfo['streamerInfo']['accessLevel'],
            'authorized': 'Y'
            }
        sendObj = {}
        sendObj['requests'] = [{
            'service': 'ADMIN',
            'command': 'LOGIN',
            'requestid': str(self.requestId()),
            'account': streamInfo['accounts'][0]['accountId'],
            'source': streamInfo['streamerInfo']['appId'],
            'parameters': {
                'token': streamInfo['streamerInfo']['token'],
                'credential': urllib.parse.quote(urllib.parse.urlencode(credential)),
                'version': '1.0'
                }
            }]

        jsonString = json.dumps(sendObj, indent=4, sort_keys=True) 
        return jsonString

    
    def charthartEquityMessage(self, streamInfo):
        msg = {
            "requests": [
                {
                    "service": "CHART_EQUITY",
                    "requestid": "2",
                    "command": "SUBS",
                    "account": streamInfo['accounts'][0]['accountId'],
                    "source": streamInfo['streamerInfo']['appId'],
                    "parameters": {
                        "keys": "AAPL",
                        "fields": "0,1,2,3,4,5,6,7,8"
                    }
                }
            ]
        }
           
        jsonString = json.dumps(msg, indent=4, sort_keys=True) 
        return jsonString 
        