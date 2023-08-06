# -*- coding: utf-8 -*-
"""
Created on Tue Feb 23 18:00:00 2023

@author: yqlim
"""
import logging
logger = logging.getLogger(__name__)

from typing import Union, Dict
import uuid
import datetime
import pytz

from .enums import ENUM_OPTION_TYPE, ENUM_OPTION_STYLE
from ...spot.base import Underlying

class PricingModel(object):
    """
    Abstract Base Class for vanilla pricing models. `PricingModel` objects 
    should always be initiated with model parameters and not with the instrument
    to be priced, for consistent implementation. The instrument is then passed
    to the `PricingModel` object via the `price()` method.
    """
    def __init__(self, model_id: str):
        self.model_id = model_id

    @property
    def model_id(self) -> str:
        return self.__str_model_id

    @model_id.setter
    def model_id(self, model_id: str) -> None:
        if model_id:
            self.__str_model_id = str(model_id)
        else:
            self.__str_model_id = uuid.uuid4()
    
    def __del__(self):
        pass
    
    def __repr__(self):
        pass
        
    def __str__(self):
        pass
    
    def __len__(self):
        pass    
    
    def price(self):
        pass

class Option(object):
    """
    Each instance represents a vanilla option. Does not assume any asset class
    but instead takes parameters that have asset-class specific properties or 
    behaviour (e.g. `cost_of_carry` can take a equity.Dividend object).
    
    Attributes
    ----------
    expiration : datetime.datetime
        expiration datetime of option - if no timezone information
        is provided, utc is assumed
    strike : double
        strike price of option
    option_type : ENUM_OPTION_TYPE
        type of option (put, call and eventually exotic options)
    option_style : ENUM_OPTION_STYLE
        style of option (european, american or path_dependent)
    underlying : finance.derivatives.vanilla.base.Underlying, optional
        underlying object or any other inherited object 
        (e.g. finance.derivatives.vanilla.instruments.Security)
        (default is None, which implies a generic vanilla option)  
    option_id : str, optional
        unique identifier of the option (default is uuid.uuid4())        
    implied_volatility : dict
    price : dict
    cost_of_carry : dict
    """    
    def __init__(self, expiration: datetime.datetime,
                    strike: float, option_type: ENUM_OPTION_TYPE, 
                    option_style: ENUM_OPTION_STYLE,
                    underlying: Underlying = None,
                    option_id: str = '') -> None:
        self.expiration = expiration
        self.strike = strike
        self.option_type = option_type
        self.option_style = option_style
        self.underlying = underlying
        self.option_id = option_id

        self.implied_volatility = {'mid':None, 'bid':None, 'ask':None}
        self.price = {'mid':None, 'bid':None, 'ask':None}
        self.cost_of_carry = {'mid':None, 'bid':None, 'ask':None}

        self.reference_spot = None
    
    def __str__(self) -> str:
        return 'Option({expiration}, {strike}, {option_type}, {option_style}, {underlying}, {option_id})'.format(
            expiration=self.expiration,
            strike=self.strike,
            option_type=self.option_type,
            option_style=self.option_style,
            underlying=self.underlying,
            option_id=self.option_id
        )
    
    def __repr__(self) -> str:
        return 'Option({expiration}, {strike}, {option_type}, {option_style}, {underlying}, {option_id})'.format(
            expiration=self.expiration,
            strike=self.strike,
            option_type=self.option_type,
            option_style=self.option_style,
            underlying=self.underlying,
            option_id=self.option_id
        )    

    def __eq__(self, to_compare: 'Option') -> bool:
        return (
            (self.underlying, self.option_style.value, self.expiration, self.strike, self.option_type.value) == 
                (to_compare.underlying, to_compare.option_style.value, to_compare.expiration, to_compare.strike, to_compare.option_type.value)
        )
    
    def __ne__(self, to_compare: 'Option') -> bool:
        return (
            (self.underlying, self.option_style.value, self.expiration, self.strike, self.option_type.value) != 
                (to_compare.underlying, to_compare.option_style.value, to_compare.expiration, to_compare.strike, to_compare.option_type.value)
        )  

    def __lt__(self, to_compare: 'Option') -> bool:
        return (
            (self.underlying, self.option_style.value, self.expiration, self.strike, self.option_type.value) < 
                (to_compare.underlying, to_compare.option_style.value, to_compare.expiration, to_compare.strike, to_compare.option_type.value)
        )

    def __le__(self, to_compare: 'Option') -> bool:
        return (
            (self.underlying, self.option_style.value, self.expiration, self.strike, self.option_type.value) <= 
                (to_compare.underlying, to_compare.option_style.value, to_compare.expiration, to_compare.strike, to_compare.option_type.value)
        )   
    
    def __gt__(self, to_compare: 'Option') -> bool:
        return (
            (self.underlying, self.option_style.value, self.expiration, self.strike, self.option_type.value) > 
                (to_compare.underlying, to_compare.option_style.value, to_compare.expiration, to_compare.strike, to_compare.option_type.value)
        )

    def __ge__(self, to_compare: 'Option') -> bool:
        return (
            (self.underlying, self.option_style.value, self.expiration, self.strike, self.option_type.value) >= 
                (to_compare.underlying, to_compare.option_style.value, to_compare.expiration, to_compare.strike, to_compare.option_type.value)
        )  

    @property
    def expiration(self) -> datetime.datetime:
        return self.__dte_expiration

    @expiration.setter  
    def expiration(self, expiration: datetime.datetime) -> None:
        if isinstance(expiration, datetime.datetime):
            if not expiration.tzinfo:
                self.__dte_expiration = expiration.replace(tzinfo=pytz.utc)
            else:
                self.__dte_expiration = expiration
        else:
            raise TypeError('`expiration` must be of `datetime.datetime` type.')
    
    @property
    def expiration_timestamp(self) -> int:
        return self.expiration.timestamp()

    @property
    def strike(self) -> float:
        return self.__dbl_strike
    
    @strike.setter
    def strike(self, strike: float) -> None:
        if isinstance(strike, float):
            self.__dbl_strike = strike
        else:
            raise TypeError('`strike` must be of `float` type.')

    @property
    def option_type(self) -> ENUM_OPTION_TYPE:
        return self.__enum_option_type

    @option_type.setter
    def option_type(self, option_type: ENUM_OPTION_TYPE) -> None:
        if isinstance(option_type, ENUM_OPTION_TYPE):
            self.__enum_option_type = option_type
        else:
            raise TypeError('`option_type` must be of `ENUM_OPTION_TYPE` type.')

    @property
    def option_style(self) -> ENUM_OPTION_STYLE:
        return self.__enum_option_style

    @option_style.setter
    def option_style(self, option_style: ENUM_OPTION_STYLE) -> None:
        if isinstance(option_style, ENUM_OPTION_STYLE):
            self.__enum_option_style = option_style
        else:
            raise TypeError('`option_style` must be of `ENUM_OPTION_STYLE` type.')
    
    @property
    def underlying(self) -> Underlying:
        return self.__obj_underlying
    
    @underlying.setter
    def underlying(self, underlying: Underlying) -> None:
        if isinstance(underlying, Underlying):
            self.__obj_underlying = underlying
        else:
            raise TypeError('`underlying` must be of `Underlying` type.')
    
    @property
    def option_id(self) -> str:
        return self.__str_option_id
    
    @option_id.setter
    def option_id(self, option_id: Union[str, None]) -> None:
        if option_id:
            self.__str_option_id = str(option_id)
        else:
            self.__str_option_id = str(uuid.uuid4())

    def _check_value(self, value: Union[None, float]) -> bool:
        """
        Check that value is either `None` or `float` type. If value is of
        `float` type, check that value is non-negative.

        Parameters
        ----------
        value : float
            value to check

        Return
        ------
        bool
            `True` if value is `None` or of `float` type and non-negative
        """
        if value is None:
            return True
        
        try:
            _ = float(value)
        except:
            raise TypeError('`value` must be of `float` type.')
            return False
        
        if _ >= 0.0:
            return True
        else:
            raise ValueError('`value` must be non-negative.')
            return False

    @property
    def implied_volatility(self) -> Dict:
        return self.__dic_implied_volatility

    @implied_volatility.setter
    def implied_volatility(self, implied_volatility: Dict) -> None:
        if isinstance(implied_volatility, dict):
            if ('mid' in implied_volatility) and ('bid' in implied_volatility) and ('ask' in implied_volatility):
                self.__dic_implied_volatility = implied_volatility
            else:
                raise ValueError('`implied_volatility` must contain "mid", "bid" and "ask" keys.')
        else:
            raise TypeError('`implied_volatility` must be of `dict` type.')

    @property
    def implied_volatility_mid(self) -> Union[None, float]:
        return self.implied_volatility['mid']

    @implied_volatility_mid.setter
    def implied_volatility_mid(self, implied_volatility_mid: Union[None, float]) -> None:
        if self._check_value(implied_volatility_mid):
            self.implied_volatility['mid'] = implied_volatility_mid

    @property
    def implied_volatility_bid(self) -> Union[None, float]:
        return self.implied_volatility['bid']

    @implied_volatility_bid.setter
    def implied_volatility_bid(self, implied_volatility_bid: Union[None, float]) -> None:
        if self._check_value(implied_volatility_bid):
            self.implied_volatility['bid'] = implied_volatility_bid
    
    @property
    def implied_volatility_ask(self) -> Union[None, float]:
        return self.implied_volatility['ask']
    
    @implied_volatility_ask.setter
    def implied_volatility_ask(self, implied_volatility_ask: Union[None, float]) -> None:
        if self._check_value(implied_volatility_ask):
            self.implied_volatility['ask'] = implied_volatility_ask

    @property
    def price(self) -> Dict:
        return self.__dic_price
    
    @price.setter
    def price(self, price: Dict) -> None:
        if isinstance(price, dict):
            if ('mid' in price) and ('bid' in price) and ('ask' in price):
                self.__dic_price = price
            else:
                raise ValueError('`price` must contain "mid", "bid" and "ask" keys.')
        else:
            raise TypeError('`price` must be of `dict` type.')        

    @property
    def price_mid(self) -> Union[None, float]:
        return self.price['mid']
    
    @price_mid.setter
    def price_mid(self, price_mid: Union[None, float]) -> None:
        if self._check_value(price_mid):
            self.price['mid'] = price_mid

    @property
    def price_bid(self) -> Union[None, float]:
        return self.price['bid']

    @price_bid.setter
    def price_bid(self, price_bid: Union[None, float]) -> None:
        if self._check_value(price_bid):
            self.price['bid'] = price_bid
        
    @property
    def price_ask(self) -> Union[None, float]:
        return self.price['ask']

    @price_ask.setter
    def price_ask(self, price_ask: Union[None, float]) -> None:
        if self._check_value(price_ask):
            self.price['ask'] = price_ask

    @property
    def cost_of_carry(self) -> Dict:
        return self.__dic_cost_of_carry

    @cost_of_carry.setter
    def cost_of_carry(self, cost_of_carry: Dict) -> None:
        if isinstance(cost_of_carry, dict):
            if ('mid' in cost_of_carry) and ('bid' in cost_of_carry) and ('ask' in cost_of_carry):
                self.__dic_cost_of_carry = cost_of_carry
            else:
                raise ValueError('`cost_of_carry` must contain "mid", "bid" and "ask" keys.')
        else:
            raise TypeError('`cost_of_carry` must be of `dict` type.')        

    @property
    def cost_of_carry_mid(self) -> Union[None, float]:
        return self.cost_of_carry['mid']
    
    @cost_of_carry_mid.setter
    def cost_of_carry_mid(self, cost_of_carry_mid: Union[None, float]) -> None:
        if cost_of_carry_mid is None:
            self.cost_of_carry['mid'] = cost_of_carry_mid
        else:
            try:
                _ = float(cost_of_carry_mid)
            except:
                raise TypeError('`cost_of_carry_mid` must be of `float` type.')
            self.cost_of_carry['mid'] = cost_of_carry_mid

    @property
    def cost_of_carry_bid(self) -> Union[None, float]:
        return self.cost_of_carry['bid']
    
    @cost_of_carry_bid.setter
    def cost_of_carry_bid(self, cost_of_carry_bid: Union[None, float]) -> None:
        if cost_of_carry_bid is None:
            self.cost_of_carry['bid'] = cost_of_carry_bid
        else:
            try:
                _ = float(cost_of_carry_bid)
            except:
                raise TypeError('`cost_of_carry_bid` must be of `float` type.')
            self.cost_of_carry['bid'] = cost_of_carry_bid
    
    @property
    def cost_of_carry_ask(self) -> Union[None, float]:
        return self.cost_of_carry['ask']
    
    @cost_of_carry_ask.setter
    def cost_of_carry_ask(self, cost_of_carry_ask: Union[None, float]) -> None:
        if cost_of_carry_ask is None:
            self.cost_of_carry['ask'] = cost_of_carry_ask
        else:
            try:
                _ = float(cost_of_carry_ask)
            except:
                raise TypeError('`cost_of_carry_ask` must be of `float` type.')
            self.cost_of_carry['ask'] = cost_of_carry_ask

    @property
    def reference_spot(self) -> Union[None, float]:
        return self.__dbl_reference_spot

    @reference_spot.setter
    def reference_spot(self, reference_spot: Union[None, float]) -> None:
        if self._check_value(reference_spot):
            self.__dbl_reference_spot = reference_spot