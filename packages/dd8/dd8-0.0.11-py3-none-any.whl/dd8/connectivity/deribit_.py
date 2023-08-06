# -*- coding: utf-8 -*-
"""
Created on Tue Sep 28 08:37:00 2022

@author: yqlim
"""
import logging
logger = logging.getLogger(__name__)

from typing import Union, Any, Callable, Dict, List
import itertools
import datetime
from dateutil import parser
import pytz
import hmac
import hashlib
from uuid import uuid4
import asyncio
import numpy as np
import copy

from .base import AsyncWebsocket
from ..finance.base import Order
from ..finance.market_data.rates import ForwardCurve
from ..finance.derivatives.vanilla.instruments import OptionCrypto, ENUM_OPTION_TYPE, ENUM_OPTION_STYLE
from ..finance.spot.instruments import Cryptocurrency

class DeribitWebsocket(AsyncWebsocket):
    _END_POINT = 'wss://www.deribit.com/ws/api/v2'
    _REQUEST_PER_SECOND = 15
    _SUPPORTED_CURRENCIES = ['BTC', 'ETH']

    def __init__(self, api_key : Union[None, str] = None, 
                    api_secret : Union[None, str] = None, 
                    client_id : Union[None, str] = None) -> None:

        super().__init__(self._END_POINT, self._REQUEST_PER_SECOND)

        self.api_key = api_key
        self.api_secret = api_secret
        self.client_id = str(uuid4()) if client_id is None else client_id
        self.msg = {'jsonrpc' : '2.0',
                    'id' : self.client_id,
                    'method' : None}

    def _to_list(self, param: Union[List, str]) -> List[str]:
        if not isinstance(param, list):
            return [param]
        else:
            return param

    def _get_signature(self) -> Dict:
        """
        Generate Deribit signature.
        """
        msg = self.msg.copy()
        msg['method'] = 'public/auth'
        params = {
            'grant_type' : 'client_credentials',
            'client_id' : self.api_key,
            'client_secret' : self.api_secret
        }
        msg['params'] = params
        return msg
    
    def get_book_summary_by_currency(self, currencies: List[str], kind: str) -> Dict:
        messages = []
        currencies = self._to_list(currencies)
        for currency in currencies:
            msg = self.msg.copy()
            msg['method'] = 'public/get_book_summary_by_currency'
            params = {
                'currency' : currency,
                'kind' : kind
            }
            msg['params'] = params        
            messages.append(msg)
        return self.gather(self._get, messages)

    def get_book_summary_by_instrument(self, instrument_names: List[str]) -> Dict:
        instrument_names = self._to_list(instrument_names)
        messages = []
        for instrument_name in instrument_names:
            msg = self.msg.copy()
            msg['method'] = 'public/get_book_summary_by_instrument'
            params = {
                'instrument_name' : instrument_name
            }
            msg['params'] = params
            messages.append(msg)
        return self.gather(self._get, messages)

    def get_contract_size(self, instrument_names: List[str]) -> Dict:
        instrument_names = self._to_list(instrument_names)
        messages = []
        for instrument_name in instrument_names:
            msg = self.msg.copy()
            msg['method'] = 'public/get_contract_size'
            params = {
                'instrument_name' : instrument_name
            }
            msg['params'] = params
            messages.append(msg)
        return self.gather(self._get, messages)

    def get_currencies(self) -> Dict:
        msg = self.msg.copy()
        msg['method'] = 'public/get_currencies'
        params = {}
        msg['params'] = params
        return self.loop(self._get, msg)

    def get_delivery_prices(self, index_names: List[str], offset: int=0, count: int=10) -> Dict:
        index_names = self._to_list(index_names)
        supported_indices = ['ada_usd', 'avax_usd', 'btc_usd', 'eth_usd', 'dot_usd', 
                                'matic_usd', 'sol_usd', 'usdc_usd', 'xrp_usd', 'ada_usdc',
                                'avax_usdc', 'btc_usdc', 'eth_usdc', 'dot_usdc', 'matic_usdc',
                                'sol_usdc', 'xrp_usdc', 'btcdvol_usdc', 'ethdvol_usdc']
        supported_index_names = [index_name.strip().lower() 
                        for index_name in index_names 
                        if index_name in supported_indices]        
        if len(supported_index_names) == len(index_names):
            messages = []
            for index_name in supported_index_names:
                msg = self.msg.copy()
                msg['method'] = 'public/get_delivery_prices'
                params = {
                    'index_name' : index_name,
                    'offset' : offset,
                    'count' : count
                }            
                msg['params'] = params
                messages.append(msg)
            return self.gather(self._get, messages)
        else:
            diff = set(index_names) - set(supported_index_names)
            raise ValueError('unsupported index name(s) - {diff}'.format(diff=diff))

    def get_funding_chart_data(self, instrument_names: List[str], length: str) -> Dict:
        instrument_names = self._to_list(instrument_names)
        supported_length = ['8h', '24h', '1m']
        if length in supported_length:
            messages = []
            for instrument_name in instrument_names:
                msg = self.msg.copy()
                msg['method'] = 'public/get_funding_chart_data'
                params = {
                    'instrument_name' : instrument_name,
                    'length' : length
                }
                msg['params'] = params
                messages.append(msg)
            return self.gather(self._get, messages)
        else:
            raise ValueError('unsupported length - {length}'.format(length=length))
    
    def get_funding_rate_history(self, instrument_names: List[str], start_timestamp: int,
                                    end_timestamp: int) -> Dict:
        instrument_names = self._to_list(instrument_names)
        messages = []
        for instrument_name in instrument_names:
            msg = self.msg.copy()
            msg['method'] = 'public/get_funding_rate_history'
            params = {
                'instrument_name' : instrument_name,
                'start_timestamp' : start_timestamp,
                'end_timestamp' : end_timestamp
            }
            msg['params'] = params
            messages.append(msg)
        return self.gather(self._get, messages)

    def get_funding_rate_value(self, instrument_names: List[str], start_timestamp: int, 
                                    end_timestamp: int) -> Dict:
        instrument_names = self._to_list(instrument_names)
        messages = []
        for instrument_name in instrument_names:
            msg = self.msg.copy()
            msg['method'] = 'public/get_funding_rate_value'
            params = {
                'instrument_name' : instrument_name,
                'start_timestamp' : start_timestamp,
                'end_timestamp' : end_timestamp
            }
            msg['params'] = params
            messages.append(msg)
        return self.gather(self._get, messages)

    def get_historical_volatility(self, currencies: List[str]) -> Dict:
        currencies = self._to_list(currencies)
        messages = []
        for currency in currencies:
            msg = self.msg.copy()
            msg['method'] = 'public/get_historical_volatility'
            params = {
                'currency' : currency
            }
            msg['params'] = params
            messages.append(msg)
        return self.gather(self._get, messages)

    def get_index_price(self, index_names: List[str]) -> Dict:
        index_names = self._to_list(index_names)
        messages = []
        for index_name in index_names:
            msg = self.msg.copy()
            msg['method'] = 'public/get_index_price'
            params = {
                'index_name' : index_name
            }
            msg['params'] = params
            messages.append(msg)
        return self.gather(self._get, messages)

    def get_index_price_names(self) -> Dict:
        msg = self.msg.copy()
        msg['method'] = 'public/get_index_price_names'
        params = {
        }
        msg['params'] = params
        return self.loop(self._get, msg)

    def get_instrument(self, instrument_names: List[str]):
        instrument_names = self._to_list(instrument_names)
        messages = []
        for instrument_name in instrument_names:
            msg = self.msg.copy()
            msg['method'] = 'public/get_instrument'
            params = {
                'instrument_name' : instrument_name
            }
            msg['params'] = params
            messages.append(msg)
        return self.gather(self._get, messages)
    
    def get_instruments(self, currencies: List[str], kind: str='', 
                            expired: bool=False) -> Dict:
        """
        Get instruments listed on Deribit.

        Parameters
        ----------
        currency : str
            underlying of instrument - must be one of `DeribitWebsocket._SUPPORTED_CURRENCIES`
        kind : str
            type of instrument - must be one of `DeribitWebsocket._SUPPORT_INSTRUMENT`
        expired : bool
            filter condition for instruments to be returned by API

        Return
        ------
        list of dict
            each dictionary is a json representation of a future object
        """
        currencies = self._to_list(currencies)
        messages = []
        for currency in currencies:
            msg = self.msg.copy()
            msg['method'] = 'public/get_instruments'
            params = {
                'currency' : currency,                
                'expired' : expired
            }
            if kind:
                params['kind'] = kind
            msg['params'] = params
            messages.append(msg)
        return self.gather(self._get, messages)

    def get_last_settlements_by_currency(self, currencies: List[str], type_: str,
                                            count: int, continuation: str,
                                            search_start_timestamp: int) -> Dict:
        currencies = self._to_list(currencies)
        messages = []
        for currency in currencies:
            msg = self.msg.copy()
            msg['method'] = 'public/get_last_settlements_by_currency'
            params = {
                'currency' : currency,
                'type' : type_,
                'count' : count,
                'continuation' : continuation,
                'search_start_timestamp' : search_start_timestamp
            }
            msg['params'] = params
            messages.append(msg)
        return self.gather(self._get, messages)

    def get_last_settlements_by_instrument(self, instrument_names: List[str], type_: str,
                                            count: int, continuation: str, 
                                            search_start_timestamp: int) -> Dict:
        instrument_names = self._to_list(instrument_names)
        messages = []
        for instrument_name in instrument_names:
            msg = self.msg.copy()
            msg['method'] = 'public/get_last_settlements_by_instrument'
            params = {
                'instrument_name' : instrument_name,
                'type' : type_,
                'count' : count,
                'continuation' : continuation,
                'search_start_timestamp' : search_start_timestamp
            }
            msg['params'] = params
            messages.append(msg)
        return self.gather(self._get, messages)

    def get_last_trades_by_currency(self, currencies: List[str], kind: str,
                                        start_id: str, end_id: str, count: int,
                                        include_old: bool, sorting: str) -> Dict:
        currencies = self._to_list(currencies)
        messages = []
        for currency in currencies:
            msg = self.msg.copy()
            msg['method'] = 'public/get_last_trades_by_currency'
            params = {
                'currency' : currency,
                'kind' : kind,
                'count' : count,
                'include_old' : include_old,
                'sorting' : sorting
            }
            if start_id:
                params['start_id'] = start_id
            if end_id:
                params['end_id'] = end_id

            msg['params'] = params
            messages.append(msg)
        
        return self.gather(self._get, messages)

    def get_last_trades_by_currency_and_time(self, currencies: List[str], 
                                        start_timestamp: int, end_timestamp: int, 
                                        kind: str = 'any', count: int = 10, 
                                        include_old: bool = False, 
                                        sorting: str = 'default') -> Dict:
        currencies = self._to_list(currencies)
        messages = []
        for currency in currencies:
            msg = self.msg.copy()
            msg['method'] = 'public/get_last_trades_by_currency_and_time'
            params = {
                'currency' : currency,
                'kind' : kind,
                'start_timestamp' : start_timestamp,
                'end_timestamp' : end_timestamp,
                'count' : count,
                'include_old' : include_old,
                'sorting' : sorting
            }
            msg['params'] = params
            messages.append(msg)
        return self.gather(self._get, messages)

    def get_last_trades_by_instrument(self, instrument_names: List[str], 
                                        start_seq: int = -99, end_seq: int = -99,
                                        count: int = 10, include_old: bool = False,
                                        sorting: str = 'default') -> Dict:
        instrument_names = self._to_list(instrument_names)
        messages = []
        for instrument_name in instrument_names:
            msg = self.msg.copy()
            msg['method'] = 'public/get_last_trades_by_instrument'
            params = {
                'instrument_name' : instrument_name,
                'count' : count,
                'include_old' : include_old,
                'sorting' : sorting
            }
            if start_seq != -99:
                params['start_seq'] = start_seq
            if end_seq != -99:
                params['end_seq'] = end_seq
            msg['params'] = params
            messages.append(msg)
        return self.gather(self._get, messages)
    
    def get_last_trades_by_instrument_and_time(self, instrument_names: List[str],
                                        start_timestamp: int, end_timestamp: int,
                                        count: int = 10, include_old: bool = False,
                                        sorting: str = 'default') -> Dict:
        instrument_names = self._to_list(instrument_names)
        messages = []
        for instrument_name in instrument_names:
            msg = self.msg.copy()
            msg['method'] = 'public/get_last_trades_by_instrument_and_time'
            params = {
                'instrument_name' : instrument_name,
                'start_timestamp' : start_timestamp,
                'end_timestamp' : end_timestamp,
                'count' : count,
                'include_old' : include_old,
                'sorting' : sorting
            }
            msg['params'] = params
        messages.append(msg)
        return self.gather(self._get, messages)

    def get_mark_price_history(self, instrument_names: List[str],
                                start_timestamp: int, end_timestamp: int) -> Dict:
        instrument_names = self._to_list(instrument_names)
        messages = []
        for instrument_name in instrument_names:
            msg = self.msg.copy()
            msg['method'] = 'public/get_mark_price_history'
            params = {
                'instrument_name' : instrument_name,
                'start_timestamp' : start_timestamp,
                'end_timestamp' : end_timestamp
            }
            msg['params'] = params
            messages.append(msg)
        return self.gather(self._get, messages)

    def get_order_book(self, instrument_names: List[str], depth: int = -99) -> Dict:
        instrument_names = self._to_list(instrument_names)
        messages = []
        for instrument_name in instrument_names:
            msg = self.msg.copy()
            msg['method'] = 'public/get_order_book'
            params = {
                'instrument_name' : instrument_name
            }
            if depth != -99:
                params['depth'] = depth
            msg['params'] = params
            messages.append(msg)        
        #return asyncio.run(self.gather(self._get, messages))
        order_books = self.gather(self._get, messages)
        return order_books

    def get_order_book_by_instrument_id(self, instrument_ids: List[int],
                                            depth: int = -99) -> Dict:
        instrument_ids = self._to_list(instrument_ids)
        messages = []
        for instrument_id in instrument_ids:
            msg = self.msg.copy()
            msg['method'] = 'public/get_order_book_by_instrument_id'
            params = {
                'instrument_id' : instrument_id
            }
            if depth != -99:
                msg['depth'] = depth
            messages.append(msg)
        return self.gather(self._get, messages)

    def get_rfqs(self, currencies: List[str], kind: str = '') -> Dict:
        currencies = self._to_list(currencies)
        messages = []
        for currency in currencies:
            msg = self.msg.copy()
            msg['method'] = 'public/get_rfqs'
            params = {
                'currency' : currency
            }
            if kind:
                params['kind'] = kind
            msg['params'] = params
            messages.append(msg)
        return self.gather(self._get, messages)
    
    def get_trade_volumes(self, extended: bool = False) -> Dict:
        msg = self.msg.copy()
        msg['method'] = 'public/get_trade_volumes'
        params = {
            'extended' : extended
        }
        msg['params'] = params
        return self.loop(self._get, msg)
    
    def get_tradingview_chart_data(self, instrument_names: List[str], 
                                start_timestamp: int, end_timestamp: int,
                                resolution: str) -> Dict:
        instrument_names = self._to_list(instrument_names)
        messages = []
        for instrument_name in instrument_names:
            msg = self.msg.copy()
            msg['method'] = 'public/get_tradingview_chart_data'
            params = {
                'instrument_name' : instrument_name,
                'start_timestamp' : start_timestamp,
                'end_timestamp' : end_timestamp,
                'resolution' : resolution
            }
            msg['params'] = params
            messages.append(msg)
        return self.gather(self._get, messages)

    def get_volatility_index_data(self, currencies: List[str], start_timestamp: int,
                                    end_timestamp: int, resolution: str) -> Dict:
        currencies = self._to_list(currencies)
        messages = []
        for currency in currencies:
            msg = self.msg.copy()
            msg['method'] = 'public/get_volatility_index_data'
            params = {
                'currency' : currency,
                'start_timestamp' : start_timestamp,
                'end_timestamp' : end_timestamp,
                'resolution' : resolution
            }
            msg['params'] = params
            messages.append(msg)
        return self.gather(self._get, messages)

    def get_ticker(self, instrument_names: List[str]) -> Dict:
        instrument_names = self._to_list(instrument_names)
        messages = []
        for instrument_name in instrument_names:
            msg = self.msg.copy()
            msg['method'] = 'public/ticker'
            params = {
                'instrument_name' : instrument_name
            }
            msg['params'] = params
            messages.append(msg)
        return self.gather(self._get, messages)        

    def get_account_summary(self, currency: str, extended: bool=False):        
        auth = self._get_signature()
        msg = self.msg.copy()
        msg['method'] = 'private/get_account_summary'        
        params = {'currency': currency,
                    'extended' : extended}        
        msg['params'] = params        
        return self.loop(self._get, msg, auth)

    def buy(self, instrument_name: str, amount: float, order_type: str,
                reduce_only: bool, price: Union[None, float], 
                post_only: Union[None, bool] = None) -> Dict:
        auth = self._get_signature()
        msg = self.msg.copy()
        msg['method'] = 'private/buy'
        params = {
            'instrument_name' : instrument_name,
            'amount' : amount,
            'type' : order_type,
            'reduce_only' : reduce_only
        }
        if price:
            params['price'] = price
        if post_only:
            params['post_only'] = post_only        
        msg['params'] = params
        self.loop(self._get, msg, auth)

    def get_option_chain(self, currency: str) -> List[Dict]:
        instruments = self.get_instruments(currencies = [currency], 
                                            kind = 'option', 
                                            expired = False)
        instrument_names = []
        for currency in instruments:
            for instrument in currency['result']:
                instrument_names.append(instrument['instrument_name'])        
        
        order_books = self.get_order_book(instrument_names, 3)        

        instruments = []
        for response in order_books:
            instrument = DeribitInstrument()  
            instrument.from_api(response['result'])          
            instruments.append(instrument)

        return instruments
        

    def get_futures(self, currency: str, expired: bool = False):
        """
        Helper function that returns futures listed on Deribit by currency.

        Parameters
        ----------
        currency : str
            coin to which to retrieve futures
        expired : bool, optional
            to include expired instruments (default is `False`, which implies that
            expired instruments will not be included)
        """
        if currency in self._SUPPORTED_CURRENCIES:
            instruments = self.get_instruments(currency, 'future', expired)
            instruments = instruments['result']

            output = []
            for instrument in instruments:
                output.append(DeribitInstrument(instrument))

            return output
        else:
            raise ValueError('unsupported `currency`.')


    def subscribe_order_book(self, instrument_names: List[str], group: str='100',
                                depth: int=1, interval: str='100ms', 
                                func: Callable=print, auth: Dict={}) -> None:
        instrument_names = self._to_list(instrument_names)
        channels = []
        for instrument_name in instrument_names:
            channel = '.'.join(['book', instrument_name, str(group), str(depth), interval])        
            channels.append(channel)

        msg = self.msg.copy()
        msg['method'] = 'public/subscribe'        
        params = {'channels' : channels}        
        msg['params'] = params
        
        self.subscribe(self._subscribe, msg, func, auth)

    def subscribe_trades_by_currency(self, currencies: List[str], kind: str,
                                        interval: str, func: Callable=print,
                                        auth: Dict={}) -> None:
        currencies = self._to_list(currencies)
        channels = []
        for currency in currencies:
            channel = '.'.join(['trades', kind, currency, interval])
            channels.append(channel)
        
        msg = self.msg.copy()
        msg['method'] = 'public/subscribe'
        params = {
            'channels' : channels
        }
        msg['params'] = params
        self.subscribe(self._subscribe, msg, func, auth)

class DeribitInstrument(object):
    def __init__(self, attributes: Union[None, Dict[str, Any]] = None) -> None:
        if not attributes is None:
            self.from_api(attributes)

    def from_api(self, attributes: Dict[str, Any]) -> None:
        """
        Instantiates object with attributes from Deribit API output.

        Parameters
        ----------
        attributes : dict
            key-value pairs returned from Deribit endpoint
        """
        if isinstance(attributes, dict):
            for k, v in attributes.items():
                setattr(self, k, v)
        else:
            raise TypeError('`attributes` must be of `dict` type.')

class DeribitOrder(Order):
    def __init__(self, instrument_name: str, amount: float, type_: str,
                    label: str, price: float, time_in_force: str, max_show: float = 0.0,
                    post_only: bool = True, reject_post_only: bool = True,
                    reduce_only: bool = False, trigger_price: float = None,
                    trigger_offset: float = None, trigger: str = '',
                    advanced: str = '', mmp: bool = False, valid_until: int = 0):
        super().__init__(instrument_name, amount, price)
        self.instrument_name = instrument_name
        self.amount = amount 
    
    @property
    def instrument_name(self) -> str:
        return self.symbol

    @property
    def amount(self) -> float:
        return self.quantity
    

def build_forward_curve(underlying: List[str]) -> ForwardCurve:
    """
    Build forward curves from Deribit for given underlying.

    Parameters
    ----------
    underlying : list of str
        underlying with fixed maturity futures listed on Deribit
    
    Return
    ------
    dict
        dictionary containing mid, bid and ask `ForwardCurve` objects in 
        the format of `{underlying: {'mid':ForwardCurve, 'bid':ForwardCurve, 'ask':ForwardCurve}}`
    """
    # check inputs
    if isinstance(underlying, str):
        underlying = [underlying]    
    underlying = [und.strip().upper() for und in underlying]
    instrument_names = {und.strip().upper():[] for und in underlying}
    
    # get fixed maturity futures instrument names    
    client = DeribitWebsocket()
    summary = client.get_book_summary_by_currency(underlying, 'future')

    # get benchmark indices of fixed maturity 
    indices = []
    for i in range(len(underlying)):
        index = []
        for instrument in summary[i]['result']:
            index.append('_'.join([
                                instrument['base_currency'].strip().lower(),
                                instrument['quote_currency'].strip().lower()]
                                )
            )
            if not 'PERPETUAL' in instrument['instrument_name']:
                instrument_names[instrument['base_currency']].append(instrument)
        index = list(set(index))
        indices += index
        
    index_prices = client.get_index_price(indices)
    index_prices = [float(idx['result']['index_price']) for idx in index_prices] 
    
    curves = {und.strip().upper():{'bid':None, 'ask':None, 'mid':None} for und in underlying}
    for i in range(len(underlying)):
        dates = []
        mid_prices = []
        bid_prices = []
        ask_prices = []
        und = underlying[i].strip().upper()
        for data in instrument_names[und]:
            instrument_name = data['instrument_name']
            uid = '.'.join([und, 'FORWARD'])
            expiry = parser.parse(instrument_name.split('-')[1]).replace(hour=8, minute=0, second=0, tzinfo=pytz.utc) 
            dates.append(expiry)

            mid_prices.append(data['mid_price'])
            bid_prices.append(data['bid_price'])
            ask_prices.append(data['ask_price'])
        
        forward_curve = ForwardCurve(dates=np.array(dates), prices=np.array(mid_prices), curve_id=uid+'.MID')
        forward_curve.calibrate(index_prices[i])        
        curves[und]['mid'] = forward_curve

        forward_curve = ForwardCurve(dates=np.array(dates), prices=np.array(bid_prices), curve_id=uid+'.BID')
        forward_curve.calibrate(index_prices[i])        
        curves[und]['bid'] = forward_curve

        forward_curve = ForwardCurve(dates=np.array(dates), prices=np.array(ask_prices), curve_id=uid+'.ASK')
        forward_curve.calibrate(index_prices[i])        
        curves[und]['ask'] = forward_curve

    return curves

def create_option(instrument_name: str) -> OptionCrypto:
    """
    Function to create an instance of `OptionCrypto` using 
    instrument name from Deribit.

    Parameters
    ----------
    instrument_name : str
        instrument name from Deribit API
    
    Return
    ------
    OptionCrypto
        an instance of `OptionCrypto`
    """
    underlying, expiration, strike, option_type = instrument_name.split('-')  
    underlying = Cryptocurrency(underlying)
    expiration = parser.parse(expiration)
    expiration = expiration.replace(hour=8, minute=0, second=0, tzinfo=pytz.utc)
    option_type = option_type.strip().upper()
    if option_type == 'P':
        option_type = ENUM_OPTION_TYPE.PUT
    elif option_type == 'C':  
        option_type = ENUM_OPTION_TYPE.CALL
    else:
        raise NotImplementedError('`option_type` not implemented.')  
    return OptionCrypto(expiration=expiration, 
                            strike=float(strike), 
                            option_type=option_type, 
                            option_style=ENUM_OPTION_STYLE.EUROPEAN,
                            underlying = underlying)

def build_option_chain(underlying: List[str]) -> List[OptionCrypto]:
    client = DeribitWebsocket()
    instruments = client.get_instruments(currencies = underlying, 
                                        kind = 'option', 
                                        expired = False)
    instrument_names = []
    for currency in instruments:
        for instrument in currency['result']:
            instrument_names.append(instrument['instrument_name'])        
    
    order_books = client.get_order_book(instrument_names, 3)        

    instruments = []
    for response in order_books:
        instrument = response['result']
        option = create_option(instrument['instrument_name'])        
        bid_price = float(instrument['bids'][0][0]) if instrument['bids'] else 0.0        
        ask_price = float(instrument['asks'][0][0]) if instrument['asks'] else 0.0
        option.price = {
            'bid' : bid_price,
            'ask' : ask_price,
            'mid' : (bid_price + ask_price) / 2.0
        }
        instruments.append(option)
        
    return instruments
