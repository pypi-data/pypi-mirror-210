# -*- coding: utf-8 -*-
"""
Created on Tue Jan 17 13:00:00 2023

@author: yqlim
"""
import logging
logger = logging.getLogger(__name__)

import datetime
from ..base import RequestForQuote

class RequestForQuoteVanilla(RequestForQuote):
    """
    An instance of a pricing request for vanilla options (including vanilla spreads).
    Supported product types include European Call, European Put.
    """
    _SUPPORTED_TYPES = ['P', 'C', 'PS', 'CS', 'CCAL', 'PCAL', 'CFLY', 'PFLY', 'CUST']
    def __init__(self, requestor: str = '', request_id: str = '') -> None:
        """
        Parameters
        ----------
        instrument : str
            option details in the format of {underlying}|{expiry}|{strike}|{type}|{style}.
        delimiter : str, optional
            string used to split instrument into components (default is '|')
        requestor : str, optional
            source of request (default is '')
        request_id : str, optional
            uuid of request (default is uuid.uuid4())
        """
        super().__init__(requestor, request_id)
        
        # initial values
        self.request = ''
        self.trade_details = ''        
        self.spread = None
        
        # processed values
        self.underlying =  ''
        self.product_type = ''
        
        self.spot_reference = dict()
        self.volatility_spread = dict()
        self.volatility_spread_from_mid = True        

        self.legs = []
        self.position_mapping = dict()

        self.greeks = dict()
        self.price_usd = dict()
        self.price_underlying = dict()

        self.timestamp_creation = datetime.datetime.now()
        self.timestamp_response = None

    def __repr__(self) -> str:
        return 'RequestForQuoteVanilla({requestor}, {request_id})'.format(requestor = self.requestor, request_id = self.request_id)

    def set_volatility_spread(self, bid_volatility_spread: float = 0.0, 
                                ask_volatility_spread: float = 0.0, 
                                from_mid: bool = True) -> None:
        """
        Volatility spread to determine bid/ask price of option.

        Parameters
        ----------
        bid_volatility_spread : float, optional
            volatility spread to determine bid price of option (default is 0).
            a positive spread will give a more passive bid while a negative
            spread will give a more aggressive bid.
        ask_volatility_spread : float, optional
            volatility spread to determine ask price of option (default is 0).
            a positive spread will give a more passive ask while a negative
            spread will give a more aggressive ask.
        from_mid : bool, optional
            to apply volatility spread from mid volatility, else volatility 
            spread will be applied to market bid/ask volatility (default is True).
        """
        self.volatility_spread['bid'] = bid_volatility_spread
        self.volatility_spread['ask'] = ask_volatility_spread
        self.volatility_spread_from_mid = from_mid

    def set_spot_reference(self, bid: float, ask: float) -> None:
        self.spot_reference['bid'] = bid
        self.spot_reference['ask'] = ask
        
    def is_valid(self, instrument: str, delimiter: str) -> bool:
        """
        Validate instrument contains 5 components delimited by specified delimiter.
        In addition, attempt to parse option expiry using `dateutil.parser.parse`.

        Parameters
        ----------
        instrument: str
            option details in the format of {underlying}|{expiry}|{strike}|{type}|{style}.
        delimiter : str
            string used to split instrument into components.

        Return
        ------
        bool
            `True` if instrument is valid.
        """
        self.details = instrument.strip().split(delimiter)
        if not len(self.details) == 5:
            raise ValueError('`instrument` should contain 5 components separated by `delimiter`.')
            return False
        return True


        
        