# -*- coding: utf-8 -*-
"""
Created on Wed Feb 22 08:37:00 2023

@author: yqlim
"""
import logging
logger = logging.getLogger(__name__)

from typing import Union, Any, Dict, List
import uuid
import hmac
import hashlib

from .base import AsyncConnection

class BitRest(AsyncConnection):
    _END_POINT = 'https://api.bit.com'
    _REQUESTS_PER_SECOND = 10

    def __init__(self, api_key: Union[None, str] = None,
                        api_secret: Union[None, str] = None,
                        client_id: Union[None, str] = None) -> None:
        super().__init__(self._REQUESTS_PER_SECOND)
        self.api_key = api_key
        self.api_secret = api_secret
        self.client_id = str(uuid.uuid4()) if client_id is None else client_id

        self.headers = {
            'Content-Type':'application/json'
        }

    def _encode_list(self, to_encode: List) -> str:
        result = []
        for item in to_encode:
            value = self._encode_object(item)
            result.append(value)
        output = '&'.join(result)
        output = '[' + output + ']'
        return output

    def _encode_object(self, to_encode: Any) -> Union[str, int]:
        if isinstance(to_encode, (str, int)):
            return to_encode

        if isinstance(to_encode, dict):
            sorted_keys = to_encode.keys()
            result = []
            for key in sorted_keys:
                value = to_encode[key]
                if isinstance(value, list):
                    value = self._encode_list(value)                    
                elif isinstance(value, dict):
                    value = self._encode_object(value)
                elif isinstance(value, bool):
                    value = str(value).lower()
                else:
                    value = str(value)
                result.append('{key}={value}'.format(key=key, value=value))

            sorted_list = sorted(result)
            output = '&'.join(sorted_list)
            return output    
        else:
            raise TypeError('`value` must be of `str`, `int` or `dict` type.``')
            return ''

    def _get_signature(self, method: str, path: str, params: Dict) -> None:
        signature = path + '&' + self._encode_object(params)
        signature = hmac.new(self.api_secret.encode('utf-8'), 
                                signature.encode('utf-8'), digestmod=hashlib.sha256).hexdigest()
        return signature

    def get_index(self, quote_currencies: List[str], base_currency: str = '') -> Dict:
        path = self._END_POINT + '/um/v1/index_price'
        messages = []
        params = []
        headers = []
        for quote_currency in quote_currencies:
            messages.append(path)
            params.append(
                {
                    'quote_currency' : quote_currency,
                    'currency' : base_currency
                }
            )
            headers.append(self.headers)

        return self.gather(self._get, messages, params, headers)
    

