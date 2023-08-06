import logging
logger = logging.getLogger(__name__)

from typing import Dict
import uuid
import json
from .base import AsyncConnection

## https://github.com/danpaquin/coinbasepro-python/blob/master/cbpro/public_client.py

class CoinbaseRest(AsyncConnection):
    _END_POINT = 'https://api.exchange.coinbase.com/'
    _REQUEST_PER_SECOND = 10

    def __init__(self, api_key: str = '', api_secret: str ='',
                    client_id: str = '') -> None:
        super().__init__(CoinbaseRest._END_POINT)
        self.api_key = api_key
        self.api_secret = api_secret
        self.client_id = client_id

    def _get_headers(self) -> Dict:
        return {
            'Accept' : 'application/json'
        }

    def get_trading_pairs(self) -> Dict:
        url = self._END_POINT + 'products/'
        headers = self._get_headers()
        return self.loop(self._get, url, headers=headers)

    def get_order_book(self, currency: str, level: int = 3) -> Dict:
        url = self._END_POINT + 'products/{currency}/book?level={level}'
        url = url.format(currency = currency.strip().upper(), level=level)
        headers = self._get_headers()        
        return self.loop(self._get, url, headers=headers)

    @property
    def client_id(self) -> str:
        return self.__str_client_id

    @client_id.setter
    def client_id(self, client_id) -> None:
        if client_id:
            self.__str_client_id = str(client_id)
        else:
            self.__str_client_id = str(uuid.uuid4())