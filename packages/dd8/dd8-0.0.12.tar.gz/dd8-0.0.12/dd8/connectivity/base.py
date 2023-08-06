# -*- coding: utf-8 -*-
"""
Created on Tue Aug  9 12:23:41 2022

@author: yqlim
"""

from typing import Union, List, Dict, Callable
import datetime
import time
import json
import asyncio
from aiohttp import ClientSession
import websockets

class AsyncConnection(object):
    def __init__(self, request_per_second: int = 0) -> None:
        self.request_per_second = request_per_second

    async def _get(self, url: str, params: Dict = {}, headers: Dict = {}) -> Dict:
        async with ClientSession() as sess:
            async with sess.get(url, params=params, headers=headers) as resp:
                response = await resp.json()
        await asyncio.sleep(0.15)
        return response

    async def _post(self, url: str, data: Dict = {}, headers: Dict = {}) -> Dict:
        async with ClientSession() as sess:
            async with sess.post(url, data=data, headers=headers) as resp:
                response = await resp.json()
        await asyncio.sleep(0.15)
        return response

    async def _put(self, url: str, data: Dict = {}, headers: Dict = {}) -> Dict:
        async with ClientSession() as sess:
            async with sess.put(url, data=data, headers=headers) as resp:
                response = await resp.json()
        await asyncio.sleep(0.15)
        return response

    async def _patch(self, url: str, data: Dict = {}, headers: Dict = {}) -> Dict:
        async with ClientSession() as sess:
            async with sess.patch(url, data=data, headers=headers) as resp:
                response = await resp.json()
        await asyncio.sleep(0.15)
        return response

    async def _delete(self, url: str, data: Dict = {}, headers: Dict = {}) -> Dict:
        async with ClientSession() as sess:
            async with sess.delete(url, data=data, headers=headers) as resp:
                response = await resp.json()
        await asyncio.sleep(0.15)
        return response

    def _is_list(self, messages: List, params: List) -> bool:
        """
        Check `params` is either of `list` or `dict` type. If `params` is of `list`
        type, check that `params` has the same length as `messages`.
        """
        if isinstance(params, list):
            if len(messages) != len(params):
                raise ValueError('length of `params` must match that of `messages`')
            else:
                return True
        elif isinstance(params, dict):
            return False
        else:
            raise ValueError('`params` must be of `list` or `dict` type.')

    async def _gather(self, messages: List[Callable]) -> List[Dict]:                
        return await asyncio.gather(*messages)

    def gather(self, requestor: Callable, messages: List[str], params: Union[Dict, List[Dict]] = {},
                            headers: Union[Dict, List[Dict]] = {}) -> List[Dict]:
        params_is_list = self._is_list(messages, params)
        headers_is_list = self._is_list(messages, headers)
        messages = [json.dumps(msg) if not isinstance(msg, str) else msg for msg in messages ]
        
        if (not params_is_list) and (not headers_is_list):
            combined = [requestor(msg, params, headers) for msg in messages]
        elif (params_is_list) and (not headers_is_list):
            combined = []
            for i in range(len(messages)):
                combined.append(requestor(messages[i], params[i], headers))
        elif (not params_is_list) and headers_is_list:
            combined = []
            for i in range(len(messages)):
                combined.append(requestor(messages[i], params, headers[i]))
        elif params_is_list and headers_is_list:
            combined = []
            for i in range(len(messages)):
                combined.append(requestor(messages[i], params[i], headers[i]))
           
        if self.request_per_second:          
            num_of_messages = len(combined)       
                    
            if num_of_messages <= self.request_per_second:        
                responses = asyncio.run(self._gather(combined))
            else:                              
                start = 0
                end = self.request_per_second
                responses = []
                while end <= num_of_messages:
                    current_messages = combined[start : end]
                    now = datetime.datetime.now()
                    response = asyncio.run(self._gather(current_messages))
                    responses += response

                    start += self.request_per_second
                    end += self.request_per_second

                    duration = (datetime.datetime.now() - now).total_seconds()
                    if duration < 1.0:
                        time.sleep(1.0 - duration)                    
        else:            
            responses = asyncio.run(self._gather(combined))
        return responses        
    
    def loop(self, method: Callable, payload: Union[Dict, str], params: Dict = {}, headers: Dict = {}) -> Dict:   
        if not isinstance(payload, str):
            payload = json.dumps(payload)     
        response = asyncio.run(method(payload, params, headers))
        return response

class AsyncWebsocket(AsyncConnection):
    def __init__(self, endpoint: str, request_per_second: int = 0) -> None:
        super().__init__(request_per_second)
        self.endpoint = endpoint

    async def _get(self, payload: Union[Dict, str], params: Union[Dict, List[Dict]] = {},
                            headers: Union[Dict, List[Dict]] = {}, auth: Dict = {}) -> Dict:
        async with websockets.connect(self.endpoint) as websocket:
            if auth:
                await websocket.send(json.dumps(auth))
                while websocket.open:
                    response = await websocket.recv()                    
                    await websocket.send(payload)
                    while websocket.open:
                        response = await websocket.recv()
                        response = json.loads(response)
                        break
                    return response
            else:
                await websocket.send(payload)
                while websocket.open:
                    response = await websocket.recv()
                    response = json.loads(response)
                    break
                return response

    async def _subscribe(self, payload: Union[Dict, str], 
                            func: Callable, auth: Dict = {}) -> None:
        if auth:
            async with websockets.connect(self.endpoint) as websocket:            
                await websocket.send(json.dumps(auth))
                while websocket.open:
                    response = await websocket.recv()
                    await websocket.send(payload)
                    while websocket.open:
                        response = await websocket.recv()
                        response = json.loads(response)
                        func(response)
        else:
            async with websockets.connect(self.endpoint) as websocket:
                await websocket.send(payload)
                while websocket.open:
                    response = await websocket.recv()
                    response = json.loads(response)                    
                    func(response)

    def subscribe(self, subscription: Callable, payload: Union[Dict, str], 
                    func: Callable, auth: Dict={}) -> None:
        if not isinstance(payload, str):
            payload = json.dumps(payload)
        asyncio.run(subscription(payload, func, auth))


