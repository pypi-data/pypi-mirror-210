import logging
logger = logging.getLogger(__name__)

from typing import Callable, Dict
import uuid
import dateutil.parser
from .enums import ENUM_RESOLUTION
from .base import AsyncConnection, AsyncWebsocket

class BinanceWebsocket(AsyncWebsocket):
    _END_POINT = 'wss://testnet.binance.vision/ws-api/v3'
    _REQUEST_PER_SECOND = 10

    def __init__(self, api_key: str = '', api_secret: str = '',
                    client_id: str = '', end_point: str = '') -> None:        
        self.api_key = api_key
        self.api_secret = api_secret
        self.client_id = client_id
        self.end_point = end_point
        super().__init__(self.end_point, BinanceWebsocket._REQUEST_PER_SECOND)
        self.msg = {                        
            'params' : {},
            'id' : self.client_id
        }

    def subscribe_order_book(self, func: Callable, symbol: str, level: int) -> None:
        msg = self.msg.copy()
        msg['method'] = 'depth'
        params = {
            'symbol' : 'BNBBTC'
        }
        msg['params'] = params
        print(msg)
        self.subscribe(self._subscribe, msg, func)

    @property
    def end_point(self) -> str:
        return self.__str_end_point
    
    @end_point.setter
    def end_point(self, end_point: str) -> None:
        if end_point:
            self.__str_end_point = end_point
        else:
            self.__str_end_point = BinanceWebsocket._END_POINT
    
    @property
    def client_id(self) -> str:
        return self.__str_client_id

    @client_id.setter
    def client_id(self, client_id) -> None:
        if client_id:
            self.__str_client_id = client_id
        else:
            self.__str_client_id = str(uuid.uuid4())

class BinanceDataRest(AsyncConnection):
    """
        • The base endpoint https://data.binance.com can be used to access the following API endpoints that have NONE as security type:
        ◦ GET /api/v3/aggTrades
        ◦ GET /api/v3/avgPrice
        ◦ GET /api/v3/depth
        ◦ GET /api/v3/exchangeInfo
        ◦ GET /api/v3/klines
        ◦ GET /api/v3/ping
        ◦ GET /api/v3/ticker
        ◦ GET /api/v3/ticker/24hr
        ◦ GET /api/v3/ticker/bookTicker
        ◦ GET /api/v3/ticker/price
        ◦ GET /api/v3/time
        ◦ GET /api/v3/trades
        ◦ GET /api/v3/uiKlines
    """

    _END_POINT = 'https://data.binance.com'
    _REQUEST_PER_SECOND = 10

    def __init__(self, client_id: str = '') -> None:
        super().__init__(BinanceDataRest._REQUEST_PER_SECOND)
        self.client_id = client_id

    def _map_to_interval(self, resolution: ENUM_RESOLUTION) -> str:
        seconds = resolution.value
        # month, week, day, hour, minute, second
        seconds_per = [(2592000, 'M'), (604800, 'w'), (86400, 'd'), (3600, 'h'), (60, 'm'), (1, 's')]
        for mapping in seconds_per:
            if seconds%mapping[0] == 0:
                return str(int(seconds/mapping[0])) + mapping[1]
        return ''

    def get_historical_data(self, symbol: str, interval: ENUM_RESOLUTION, 
                                start_time: str, end_time: str) -> Dict:
        """
        Get OHLCV data.

        Parameters
        ----------
        symbol : str
            Binance spot symbol
        interval : ENUM_RESOLUTION
            data resolution
        start_time : str
            parsed to `datetime.datetime` using `dateutil.parser.parse`
        end_time : str
            parsed to `datetime.datetime` using `dateutil.parser.parse`
        
        Return
        ------
        list[list]
            time series data from oldest to newest. Example:
                [
                    [
                        1499040000000,      // Kline open time
                        "0.01634790",       // Open price
                        "0.80000000",       // High price
                        "0.01575800",       // Low price
                        "0.01577100",       // Close price
                        "148976.11427815",  // Volume
                        1499644799999,      // Kline Close time
                        "2434.19055334",    // Quote asset volume
                        308,                // Number of trades
                        "1756.87402397",    // Taker buy base asset volume
                        "28.46694368",      // Taker buy quote asset volume
                        "0"                 // Unused field, ignore.
                    ]
                ]
        """
        limit = 1000
        supported_resolution = [ENUM_RESOLUTION.SECOND_1, ENUM_RESOLUTION.MINUTE_1,
            ENUM_RESOLUTION.MINUTE_3, ENUM_RESOLUTION.MINUTE_5, ENUM_RESOLUTION.MINUTE_15,
            ENUM_RESOLUTION.MINUTE_30, ENUM_RESOLUTION.HOUR_1, ENUM_RESOLUTION.HOUR_2,
            ENUM_RESOLUTION.HOUR_4, ENUM_RESOLUTION.HOUR_6, ENUM_RESOLUTION.HOUR_8,
            ENUM_RESOLUTION.HOUR_12, ENUM_RESOLUTION.DAY_1, ENUM_RESOLUTION.DAY_3,
            ENUM_RESOLUTION.DAY_7, ENUM_RESOLUTION.DAY_30]

        if interval in supported_resolution:
            url = BinanceDataRest._END_POINT + '/api/v3/klines'
            timestamp_start = int(dateutil.parser.parse(start_time).timestamp()*1e3)
            timestamp_end = int(dateutil.parser.parse(end_time).timestamp()*1e3)
            duration = timestamp_end - timestamp_start
            interval_duration = interval.value * limit * 1e3
            interval_string = self._map_to_interval(interval)
            if timestamp_start + interval_duration > timestamp_end:
                # 1 request
                params = {
                    'symbol' : symbol,
                    'interval' : interval_string,
                    'startTime' : int(timestamp_start),
                    'endTime' : int(timestamp_end)
                }
                return self.loop(self._get, url, params=params)
            else:
                #multiple requests                
                messages = []
                params = []
                start = timestamp_start
                end = timestamp_start + interval_duration
                while end < timestamp_end:
                    param = {
                        'symbol' : symbol,
                        'interval' : interval_string,
                        'startTime' : int(start),
                        'endTime' : int(end)
                    }
                    messages.append(url)
                    params.append(param)
                    start += interval_duration
                    end += interval_duration
                param = {
                    'symbol' : symbol,
                    'interval' : interval_string,
                    'startTime' : int(start),
                    'endTime' : int(timestamp_end)
                }
                messages.append(url)
                params.append(param)
                responses = self.gather(self._get, messages=messages, params=params)
                responses = [row for response in responses for row in response]
                return responses
        else:
            raise ValueError('unsupported `interal`.')

    @property
    def client_id(self) -> str:
        return self.__str_client_id

    @client_id.setter
    def client_id(self, client_id) -> None:
        if client_id:
            self.__str_client_id = client_id
        else:
            self.__str_client_id = uuid.uuid4()
    

class BinanceRest(AsyncConnection):
    """
    General API Information
    • The base endpoint is: https://api.binance.com
    • If there are performance issues with the endpoint above, these API clusters are also available:
    ◦ https://api1.binance.com
    ◦ https://api2.binance.com
    ◦ https://api3.binance.com
    • All endpoints return either a JSON object or array.
    • Data is returned in ascending order. Oldest first, newest last.
    • All time and timestamp related fields are in milliseconds.
    • The base endpoint https://data.binance.com can be used to access the following API endpoints that have NONE as security type:
    ◦ GET /api/v3/aggTrades
    ◦ GET /api/v3/avgPrice
    ◦ GET /api/v3/depth
    ◦ GET /api/v3/exchangeInfo
    ◦ GET /api/v3/klines
    ◦ GET /api/v3/ping
    ◦ GET /api/v3/ticker
    ◦ GET /api/v3/ticker/24hr
    ◦ GET /api/v3/ticker/bookTicker
    ◦ GET /api/v3/ticker/price
    ◦ GET /api/v3/time
    ◦ GET /api/v3/trades
    ◦ GET /api/v3/uiKlines
    """
    __ENDPOINT = 'https://api.binance.com'
    __REQUEST_PER_SECOND = 0
    
    def __init__(self, api_key: str = '', api_secret: str = '',
                    client_id: str = '') -> None:
        super().__init__(BinanceRest.__REQUEST_PER_SECOND)
        self.api_key = api_key
        self.api_secret = api_secret
        self.client_id = client_id

    @property
    def client_id(self) -> str:
        return self.__str_client_id
    
    @client_id.setter
    def client_id(self, client_id) -> None:
        if client_id:
            self.__str_client_id = client_id
        else:
            self.__str_client_id = uuid.uuid4()
    