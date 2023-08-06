import logging
logger = logging.getLogger(__name__)

from typing import Union, Callable, Dict, List
import datetime
import hashlib
import hmac
import base64
import json
import asyncio

try:
    from urllib.parse import urlencode
except:
    from urllib import urlencode

from .base import AsyncConnection
from ..finance.base import Order

class TalosSecurities(object):
    pass

class TalosOrder(Order):
    def __init__(self, symbol: str, side: str, order_quantity: float,
                    order_type: str, price: float, markets: List[str], currency: str, 
                    expected_fill_quantity: float, expected_fill_price: float,
                    time_in_force: str, transact_time: str, cancel_session_id: str,
                    subaccount: str, comments: str, group: str, rfq_id: str,
                    quote_id: str, allowed_slippage: float, strategy: str,
                    parameters: Dict, end_time: str, allocation, 
                    initial_decision_status: str, client_order_id: str):
        super().__init__()
        self.symbol = symbol
        self.side = side
        self.order_quantity = order_quantity
        self.order_type = order_type
        self.price = price
        self.markets = markets
        self.currency = currency
        self.expected_fill_quantity = expected_fill_quantity
        self.expected_fill_price = expected_fill_price
        self.time_in_force = time_in_force
        self.transact_time = transact_time
        self.cancel_session_id = cancel_session_id
        self.subaccount = subaccount
        self.comments = comments
        self.group = group
        self.rfq_id = rfq_id
        self.quote_id = quote_id
        self.allowed_slippage = allowed_slippage
        self.stratgy = strategy
        self.parameters = parameters
        self.end_time = end_time
        self.allocation = allocation
        self.initial_decision_status = initial_decision_status
        self.client_order_id = client_order_id

class TalosRest(AsyncConnection):
    _SUPPORTED_METHODS = ['GET', 'POST', 'PUT', 'PATCH', 'DELETE']
    def __init__(self, api_key: str = '', api_secret: str = '', 
                    host: str = '') -> None:
        super().__init__(10)
        self.api_key = api_key
        self.api_secret = api_secret
        self.host = host        
        self.endpoint = 'https://' + self.host

    def _to_list(self, param: Union[Dict, List[Dict]]) -> List:
        if not isinstance(param, list):
            if isinstance(param, dict):
                return [param]
            else:
                raise ValueError('`param` must be a `Dict` or `List[Dict]`.')
        else:
            return param

    def _format_datetime(self, datetime_: datetime.datetime) -> str:
        return datetime_.strftime('%Y-%m-%dT%H:%M:%S.000000Z')

    def _calculate_signature(self, parts: List) -> str:
        payload = '\n'.join(parts)
        hashvalue = hmac.new(
            self.api_secret.encode('ascii'),
            payload.encode('ascii'),
            hashlib.sha256
        )
        hashvalue.hexdigest()
        signature = base64.urlsafe_b64encode(hashvalue.digest()).decode()
        return signature

    def _get_headers(self, method: str, path: str, params_string: str) -> Dict:
        method = method.strip().upper()
        if not method in self._SUPPORTED_METHODS:
            raise ValueError('unsupported method - {method}'.format(method=method))
        
        utc_now = datetime.datetime.utcnow()
        #utc_datetime = utc_now.strftime('%Y-%m-%dT%H:%M:%S.000000Z')
        utc_datetime = self._format_datetime(utc_now)
        parts = [
            method,
            utc_datetime,
            self.host,
            path
        ]
        
        if method == 'GET' or method == 'DELETE':            
            if len(params_string) > 0:
                parts.append(params_string)
        else:            
            parts.append(params_string)
            
        signature = self._calculate_signature(parts)
        headers = {
            'TALOS-KEY' : self.api_key,
            'TALOS-SIGN' : signature,
            'TALOS-TS' : utc_datetime
        }
        return headers  

    def get(self, path: str, params: List[Dict]) -> List[Dict]:
        params = self._to_list(params)
        messages = []
        headers = []
        for param in params:
            query_string = urlencode(param, safe=',:')
            header = self._get_headers('GET', path, query_string)
            url = self.endpoint + path + '?' + query_string
            messages.append(url)
            headers.append(header)

        return self.gather(self._get, messages, {}, headers)

    def post(self, path: str, params: List[Dict]) -> List[Dict]:
        params = self._to_list(params)
        messages = []
        data = []
        headers = []
        for param in params:
            json_data = json.dumps(param)
            header = self._get_headers('POST', path, json_data)
            url = self.endpoint + path
            messages.append(url)
            data.append(json_data)
            headers.append(header)
        
        return self.gather(self._post, messages, data, headers)

    def put(self, path: str, params: List[Dict]) -> List[Dict]:
        params = self._to_list(params)
        messages = []
        data = []
        headers = []
        for param in params:
            json_data = json.dumps(param)
            header = self._get_headers('PUT', path, json_data)
            url = self.endpoint + path
            messages.append(url)
            data.append(json_data)
            headers.append(header)
        
        return self.gather(self._put, messages, data, headers)     

    def patch(self, path: str, params: List[Dict]) -> List[Dict]:
        params = self._to_list(params)
        messages = []
        data = []
        headers = []
        for param in params:
            json_data = json.dumps(param)
            header = self._get_headers('PATCH', path, json_data)
            url = self.endpoint + path
            messages.append(url)
            data.append(json_data)
            headers.append(header)
        
        return self.gather(self._patch, messages, data, headers)
    
    def delete(self, path: str, params: List[Dict]) -> List[Dict]:
        params = self._to_list(params)
        messages = []
        headers = []
        for param in params:
            query_string = urlencode(param)
            header = self._get_headers('DELETE', path, query_string)
            url = self.endpoint + path + '?' + query_string
            messages.append(url)
            headers.append(header)

        return self.gather(self._delete, messages, {}, headers)

    def get_balance(self, currencies: str = '', markets: str = '', 
                        show_zero_balances: bool = False) -> List[Dict]:
        """
        Returns balance and unsettled positions vs. exchanges and dealers.
        1 row per market/account/currency.

        Parameters
        ----------
        currencies : str, optional
            comma-separated list of currency symbols (default is `''`, which implies that
            all currencies will be provided)
        markets : str, optional
            comma-separated list of markets (default is `''`, which implies that all markets
            will be provided)
        show_zero_balances : bool, optional
            includes results with zero balances (default is `False`, which implies that
            results with zero balances are excluded)
        """
        path = '/v1/balances'
        query = {
            'Currencies' : currencies,
            'Markets' : markets,
            'ShowZeroBalances' : show_zero_balances
        }
        return [resp['data'] for resp in self.get(path, query)]
        
    def get_orders(self, order_id: str = '', client_order_id: str = '', 
                        start_date: Union[None, datetime.datetime] = '',
                        end_date: Union[None, datetime.datetime] = '', 
                        statuses: str = '', rfq_id: str = '', group: str = '',
                        limit: int = 500, after: str = '') -> List[Dict]:
        """
        Get a list of orders matching the given query parameters.

        Parameters
        ----------
        order_id : str, optional
            order id to look up (default is `''`, which implies no filter)
        client_order_id : str, optional
            client order id to look up (default is `''`, which implies no filter)
        start_date : str, optional
            An ISO-8601 UTC string of the form `2019-02-13T05:17:32.000000Z`. If provided,
            will return orders that were submitted at or after this time (default is `''`, 
            which implies no filter)
        end_date : str, optional
            An ISO-8601 UTC string of the form `2019-02-13T05:17:32.000000Z`. If provided,
            will return orders that were submitted before this time (default is `''`, 
            which implies no filter)
        statuses : str, optional
            comma-separated statuses of orders to include (default is `''`, which implies 
            no filter)
        rfq_id : str, optional
            rfq_id to filter (default is `''`, which implies no filter)
        group : str, optional
            group to filter (default is `''`, which implies no filter)
        limit : int, optional
            number of records to return (defaul is 500)
        after : str, optional
            pagination : str, optional (default is `''`)

        Returns
        -------
        list of dict
            list of dictionaries of responses
        """
        if start_date:
            start_date = self._format_datetime(start_date)

        if end_date:
            end_date = self._format_datetime(end_date)

        path = '/v1/orders'
        query = {
            'OrderID' : order_id,
            'ClOrdID' : client_order_id,
            'StartDate' : start_date,
            'EndDate' : end_date,
            'Statuses' : statuses,
            'RFQID' : rfq_id,
            'Group' : group,
            'limit' : limit,
            'after' : after
        }

        initial_responses = self.get(path, query)
        paginations = [data['next'] for data in initial_responses if 'next' in data]
        while paginations:
            pages = []
            for page in paginations:
                query = {
                    'after' : page
                }
                pages.append(query)
            responses = self.get(path, pages)
            initial_responses += responses
            paginations = [data['next'] for data in responses if 'next' in data]
            
        return [details for resp in initial_responses
                    for details in resp['data']]

    def paginate(self, func: Callable, path: str, initial_query: List[Dict]):
        initial_responses = func(path, initial_query)
        paginations = [data['next'] for data in initial_responses if 'next' in data]
        while paginations:
            pages = []
            for page in paginations:
                query = {
                    'after' : page
                }
                pages.append(query)
            responses = func(path, pages)
            initial_responses += responses
            paginations = [data['next'] for data in responses if 'next' in data]
        return [resp['data'] for resp in initial_responses]

    def get_securities(self, symbols: List[str], name: str='Security') -> List[Dict]:
        path = '/v1/securities'
        if symbols:
            query = []
            for symbol in symbols:
                query.append(
                    {
                        'name' : name,
                        'Symbols' : symbol
                    }
                )
        else:
            query = [{'name' : name}]
        
        initial_responses = self.get(path, query)
        paginations = [data['next'] for data in initial_responses if 'next' in data]
        while paginations:
            pages = []
            for page in paginations:
                query = {
                    'after' : page
                }
                pages.append(query)
            responses = self.get(path, pages)
            initial_responses += responses
            paginations = [data['next'] for data in responses if 'next' in data]

        return [details for resp in initial_responses
                    for details in resp['data']]

    def cancel_orders_by_order_id(self, order_id: List[str],
                                    wait_for_status: str = 'confirmed',
                                    timeout: str = '5s') -> List[Dict]:
        """
        Cancel list of orders using `OrderID` field.

        Parameters
        ----------
        order_id : list of str
            list of `OrderID`s to cancel
        wait_for_status : str, optional
            a status to wait for before returning from the REST request - 
            can take 1 of 3 values (`pending`, `confirmed`, or `completed`)
            (default is `confirmed`, which implies REST request will be 
            returned upon confirmation of the cancellation request)
        timeout : str, optional
            duration to wait for each request to reach the requested
            status (default is `5s`)

        Returns
        -------
        list of dict
            list of dictionaries of orders            
        """
        path = '/v1/orders'
        params = []
        for uid in order_id:
            _ = {
                'OrderID' : uid,
                'wait-for-status' : wait_for_status,
                'timeout' : timeout
            }
            params.append(_)        
        orders = self.delete(path, params)
        return orders

    def cancel_orders_by_client_order_id(self, client_order_id: List[str],
                                            wait_for_status: str = 'confirmed',
                                            timeout: str = '5s') -> List[Dict]:
        """
        Cancel list of orders using `ClOrdID` field.

        Parameters
        ----------
        client_order_id : list of str
            list of `ClOrdID`s to cancel
        wait_for_status : str, optional
            a status to wait for before returning from the REST request - 
            can take 1 of 3 values (`pending`, `confirmed`, or `completed`)
            (default is `confirmed`, which implies REST request will be 
            returned upon confirmation of the cancellation request)
        timeout : str, optional
            duration to wait for each request to reach the requested
            status (default is `5s`)

        Returns
        -------
        list of dict
            list of dictionaries of orders            
        """        
        path = '/v1/orders'
        params = []
        for uid in client_order_id:
            _ = {
                'ClOrdID' : uid,
                'wait-for-status' : wait_for_status,
                'timeout' : timeout
            }
            params.append(_)        
        orders = self.delete(path, params)
        return orders

    def stage_order(self, order: TalosOrder) -> None:
        path = '/v1/orders'
        query = order.payload()
        self.post(path, query)
        

    
    
