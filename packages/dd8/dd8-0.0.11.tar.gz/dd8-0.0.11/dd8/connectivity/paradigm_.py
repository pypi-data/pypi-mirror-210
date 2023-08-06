# -*- coding: utf-8 -*-
"""
Created on Tue Jan 17 10:00:00 2023

@author: yqlim
"""
import logging
logger = logging.getLogger(__name__)

import os 
import asyncio
import base64
import hmac
import json
import pprint
import random
import sys
import time
import uuid
from urllib.parse import urljoin
from typing import Union, List, Dict, Tuple, Any
from dataclasses import dataclass

import requests
import websockets

from ..base import AsyncWebsocket
# from ..deriv.rfq import RequestForQuoteV3
# from ..deriv.distributed_ import join_queue_basic
# from ..deriv.static import TELE_CHAT_IDS

WEBSOCKET_CHANNELS = ['rfq', 'quote', 'quote_book', 'trade', 'trade_tape', 'order']

def legs_to_dict(legs: List[Dict]) -> Dict[str, Dict]:
    output = dict()
    for leg in legs:
        output[leg['instrument']] = {
            'price' : leg['price'] if 'price' in leg else 0,
            'quantity' : leg['quantity'] if 'quantity' in leg else 0,
            'side' : leg['side'] if 'side' in leg else '',
            'execution_id' : leg['exec_id'] if 'exec_id' in leg else ''
        }
    return output

@dataclass
class ParadigmTask(object):
    task_name: str = ''
    chat_id: str = ''
    user_name: str = ''
    user_id: str = ''

    details: Dict = {
        'timestamp' : -99,
        'rfq_id' : -99,
        'quote_id' : -99,
        'trade_id' : -99,
        'exec_id' : '',
        'legs' : []
    }

    def payload(self) -> Dict:
        return self.__dict__

class ParadigmWebsocket(AsyncWebsocket):
    _CHANNELS_GRFQ = ['rfq', 'quote', 'quote_book', 'trade', 'trade_tape', 'order']
    _CHANNELS_DRFQ = ['rfq', 'quote', 'trade', 'trade_confirmation']

    def __init__(self, api_key: str, api_secret: str, client_id: str = None, is_production: bool = False) -> None:
        self.api_key = api_key
        self.api_secret = api_secret
        if not client_id:
            self.client_id = str(uuid.uuid4())
        else:
            self.client_id = client_id
        
        self.is_production = is_production
        if self.is_production:
            self.host = r'wss://ws.api.prod.paradigm.trade'
        else:
            self.host = r'wss://ws.api.testnet.paradigm.trade'

        self.payload = {
            'id' : self.client_id,
            'jsonrpc' : '2.0',
            'method' : '',
            'params' : {'channel' : ''}
        }

        self.trades = dict()

    # def _sign(self, host: str, method: str, path: str, payload: Dict) -> Tuple[str, Dict, Dict]:
    #     body = json.dumps(payload).encode('utf-8')

    #     message = method.encode('utf-8') + b'\n'
    #     message += path.encode('utf-8') + b'\n'
    #     message += body

    #     timestamp = str(int(time.time() * 1000))
    #     message = timestamp.encode('utf-8') + b'\n' + message
    #     signing_key = base64.b64decode(self.api_secret)
    #     digest = hmac.digest(signing_key, message, 'sha256')
    #     signature = base64.b64.encode(digest)

    #     headers = {
    #         'Paradigm-API-Timestamp' : timestamp,
    #         'Paradigm-API-Signature' : signature,
    #         'Authorization' : 'Bearer {api_key}'.format(api_key = self.api_key)
    #     }

    #     return urljoin(host, path), headers, payload

    async def send_heartbeat(self, websocket, delay_in_seconds: int = 5) -> None:
        """
        Send a heartbeat message periodically to keep the connection alive.
        """
        heartbeat_id = 1
        payload = {
            'id' : heartbeat_id,
            'jsonrpc' : '2.0',
            'method' : 'heartbeat'
        }
        while True:
            payload['id'] = heartbeat_id
            await websocket.send(json.dumps(payload))
            heartbeat_id += 1
            await asyncio.sleep(delay_in_seconds)

    async def _listen_to_drfq(self) -> None:
        channels = ['rfq', 'quote']
        url = self.host + r'/?api-key={access_key}'
        url = url.format(access_key=self.api_key)

        async with websockets.connect(url) as websocket:
            asyncio.get_event_loop().create_task(self.send_heartbeat(websocket))
            payload = {
                'id' : self.client_id,
                'jsonrpc' : '2.0',
                'method' : 'subscribe',
                'params' : {
                    'channel' : ''
                }
            }

            for channel in channels:
                payload['params']['channel'] = channel
                await websocket.send(json.dumps(payload))
            
            while True:
                message = await websocket.recv()
                has_params = 'params' in message
                if has_params:
                    results = json.loads(message)
                    params = results['params']
                    # if params['channel'] == 'rfq' and params['data']['status'] == 'ACTIVE':
                    #     task = {
                    #         'task_name' : 'rfq_paradigm',
                    #         'chat_id' : TELE_CHAT_IDS['derivs_botroom_and_alerts'],
                    #         'user_name' : 'Deriv',
                    #         'rfq_id' : params['data']['rfq_id'],
                    #         'traded' : False,
                    #         'legs' : params['data']['legs']
                    #     }
                    #     join_queue_basic('paradigm', json.dumps(task))

        
    def listen(self, service: str) -> None:
        if service == 'drfq':
            asyncio.run(self._listen_to_drfq())
        elif service == 'traded':
            asyncio.run(self._listen_to_traded())
        elif service == 'trade_tape':
            asyncio.run(self._listen_to_trade_tape())