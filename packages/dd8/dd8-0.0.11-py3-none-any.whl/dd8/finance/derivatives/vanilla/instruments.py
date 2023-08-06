# -*- coding: utf-8 -*-
"""
Created on Tue Feb 23 18:00:00 2023

@author: yqlim
"""
import logging
logger = logging.getLogger(__name__)

import datetime

from .base import Option
from ...spot.instruments import Cryptocurrency
from .enums import ENUM_OPTION_TYPE, ENUM_OPTION_STYLE

class OptionCrypto(Option):
    def __init__(self, expiration: datetime.datetime,
                    strike: float, option_type: ENUM_OPTION_TYPE, 
                    option_style: ENUM_OPTION_STYLE = ENUM_OPTION_STYLE.EUROPEAN,
                    underlying: Cryptocurrency = None,
                    option_id: str = '') -> None:
        super().__init__(expiration, strike, option_type, option_style, underlying, option_id)        

class OptionEquity(Option):
    def __init__(self) -> None:
        pass

