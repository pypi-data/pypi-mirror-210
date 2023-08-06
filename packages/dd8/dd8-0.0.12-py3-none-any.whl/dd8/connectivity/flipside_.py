import logging
logger = logging.getLogger(__name__)

from typing import Dict
from .base import AsyncConnection

class FlipsideRest(AsyncConnection):
    _END_POINT = 'https://api.flipsidecrypto.com/api/v2'
    _REQUEST_PER_SECOND = 5

    def __init__(self):
        super().__init__(FlipsideRest._REQUEST_PER_SECOND)

    def query(self, query_id: str) -> Dict:
        url = self._END_POINT + '/queries/' + query_id + '/data/latest'
        return self.loop(self._get, url)

    