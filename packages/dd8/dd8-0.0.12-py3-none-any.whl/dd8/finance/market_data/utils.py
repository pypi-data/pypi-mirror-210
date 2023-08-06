# -*- coding: utf-8 -*-
"""
Created on Tue Jan 20 15:00:00 2023

@author: yqlim
"""
import logging
logger = logging.getLogger(__name__)

import datetime
from .enums import ENUM_DAYCOUNT_CONVENTION

def year_fraction(as_at: datetime.datetime, 
    daycount_convention: ENUM_DAYCOUNT_CONVENTION) -> float:
    numerator, denominator = daycount_convention.value.split('/')
    duration = ((dates - as_at).astype('timedelta64[ms]').astype(float)/1000.0)/86400.0
    
    if denominator == 'ACT':
        denominator = ((as_at + relativedelta(years=1)) - as_at).total_seconds() / 86400.0
    else:
        denominator = int(denominator)
    
    if numerator == 'ACT':
        numerator = duration
    else:
        numerator = int(numerator)
    
    year_fraction = numerator / denominator      