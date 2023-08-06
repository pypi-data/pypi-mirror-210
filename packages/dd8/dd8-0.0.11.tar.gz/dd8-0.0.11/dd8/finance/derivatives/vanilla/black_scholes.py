# -*- coding: utf-8 -*-
"""
Created on Tue Feb 23 18:00:00 2023

@author: yqlim
"""

import logging
logger = logging.getLogger(__name__)

from typing import Union, List
import datetime
import pytz
from .base import PricingModel, Option
from ...market_data.enums import ENUM_DAYCOUNT_CONVENTION
from ...market_data.rates import ForwardCurve
from ...market_data.volatility import VolatilitySurface

class BlackScholesMertonModel(PricingModel):
    """
    Implements the generalized Black-Scholes-Merton model for pricing of European
    options.
    
    Attributes
    ----------
    option : vanilla.VanillaOption
        vanilla European option object    
        
    Methods
    -------
    price
    """    
    def __init__(self, pricing_datetime: Union[datetime.datetime, None] = None, 
                    reference_spot: Union[float, None] = None,
                    forward_curve: Union[ForwardCurve, None] = None, 
                    volatility_surface: Union[VolatilitySurface, None] = None,
                    daycount_convention: ENUM_DAYCOUNT_CONVENTION = ENUM_DAYCOUNT_CONVENTION.ACT_365,
                    model_id: str = '') -> None:
        super().__init__(model_id)

        self.pricing_datetime = None
        self.reference_spot = None
        self.forward_curve = None
        self.volatility_surface = None

    @property
    def pricing_datetime(self) -> Union[datetime.datetime, None]:
        return self.__dte_pricing_datetime
    
    @pricing_datetime.setter
    def pricing_datetime(self, pricing_datetime: Union[datetime.datetime, None]) -> None:             
        if isinstance(pricing_datetime, datetime.datetime) or (pricing_datetime is None):
            if not pricing_datetime.tzinfo:
                self.__dte_pricing_datetime = pricing_datetime.replace(tzinfo=pytz.utc)
            else:
                self.__dte_pricing_datetime = pricing_datetime
        else:
            raise TypeError('`BlackScholesMertonModel.pricing_datetime` must be of `datetime.datetime` type.')

    @property
    def reference_spot(self) -> Union[float, None]:
        return self.__dbl_reference_spot
    
    @reference_spot.setter
    def reference_spot(self, reference_spot) -> None:        
        if isinstance(reference_spot, float) or (reference_spot is None):
            self.__dbl_reference_spot = reference_spot
        else:
            raise TypeError('`BlackScholesMertonModel.reference_spot` must be of `float` type.')

    @property
    def forward_curve(self) -> Union[ForwardCurve, None]:
        return self.__obj_forward_curve

    @forward_curve.setter
    def forward_curve(self, forward_curve: Union[ForwardCurve, None]) -> None:        
        if isinstance(forward_curve, ForwardCurve) or (forward_curve is None):
            self.__obj_forward_curve = forward_curve
        else:
            raise TypeError('`BlackScholesMertonModel.forward_curve` must be of `dd8.finance.market_data.rates.ForwardCurve` type.')

    @property
    def volatility_surface(self) -> Union[VolatilitySurface, None]:
        return self.__obj_volatility_surface
    
    @volatility_surface.setter
    def volatility_surface(self, volatility_surface: Union[VolatilitySurface, None]) -> None:
        if isinstance(volatility_surface, VolatilitySurface) or (volatility_surface is None):
            self.__obj_volatility_surface = volatility_surface
        else:
            raise TypeError('`BlackScholesMertonModel.volatility_surface` must be of `dd8.finance.market_data.volatility.VolatilitySurface` type.')

    def price(self, options: List[Option]) -> None:
        if (not self.forward_curve is None) and (not self.volatility_surface is None):  
            attributes = []      
            for option in options:
                strike = option.strike
                expiration = option.expiration
                time_to_maturity = (expiration.timestamp() - self.pricing_datetime.timestamp()) / 86400.0
                forward_rate = self.forward_curve(expiration)
                volatility = self.volatility_surface(strike, expiration)
                attributes.append([strike, ])

        else:
            raise AttributeError('`BlackScholesMertonModel.forward_curve` and `BlackScholesMertonModel.volatility_surface` needed for pricing.')

    def imply_volatility(self, options: List[Option], initial: float = 0.20) -> None:
        if not self.forward_curve is None:
            pass
        else:
            raise AttributeError('`BlackScholesMertonModel.forward_curve` needed for pricing.')

        


