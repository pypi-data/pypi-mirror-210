# -*- coding: utf-8 -*-
"""
Created on Sat May 7 23:44:49 2022

@author: yqlim
"""
import logging
logger = logging.getLogger(__name__)

import asyncio
import pandas as pd
import dateutil
from typing import Union, Dict
from .base import AsyncConnection
from ..finance.data import MarketDataHistorical

def to_timestamp(datetime_: str) -> int:    
    return dateutil.parser.parse(datetime_).timestamp()

class FtxMarketData(AsyncConnection):
    _ENDPOINT = 'https://ftx.com/api/'
    _HISTORICAL_DATA_LIMIT = 5000
    
    def __init__(self) -> None:
        super().__init__()
       
    def get_markets(self, as_dataframe: bool = True) -> Union[Dict, pd.DataFrame]:
        url = '{end_point}markets'.format(end_point = self._ENDPOINT)
        response = self.loop(self._get, url)
        if response['success']:                
            if as_dataframe:
                response = pd.DataFrame(response['result'])
            return response
        else:
            return dict()
        
    def get_historical(self, market_name: str,
                           resolution: int,
                           timestamp_start: int,
                           timestamp_end: int,
                           limit: int = 5000):
        limit = min(5000, limit)
        time_steps = (timestamp_end - timestamp_start) / resolution
        urls = []
        if time_steps <= limit:
            urls.append(
                '{end_point}markets/{market_name}/candles?resolution={resolution}&start_time={start_time}&end_time={end_time}&limit={limit}'.format(
                            end_point = self._ENDPOINT,        
                            market_name = market_name,
                            resolution = resolution,
                            start_time = timestamp_start,
                            end_time = timestamp_end,
                            limit = limit)
                )
        else:
            start = timestamp_start
            end = start + (limit * resolution)
            while end < timestamp_end:
                urls.append(
                    '{end_point}markets/{market_name}/candles?resolution={resolution}&start_time={start_time}&end_time={end_time}&limit={limit}'.format(
                                end_point = self._ENDPOINT,        
                                market_name = market_name,
                                resolution = resolution,
                                start_time = start,
                                end_time = end,
                                limit = limit)
                    )
                start = end + resolution
                end = start + (limit * resolution)
            urls.append(
                '{end_point}markets/{market_name}/candles?resolution={resolution}&start_time={start_time}&end_time={end_time}&limit={limit}'.format(
                            end_point = self._ENDPOINT,        
                            market_name = market_name,
                            resolution = resolution,
                            start_time = start,
                            end_time = end,
                            limit = limit)
                )
        responses = asyncio.run(self.gather(self._get, urls))
        responses = [pd.DataFrame(response['result']) for response in responses if 'result' in response]
        data = pd.concat(responses)        
        columns = ['time', 'open', 'high', 'low', 'close', 'volume']
        data = data.loc[:, columns]
        return MarketDataHistorical(source='ftx', data=data.values)

    
      