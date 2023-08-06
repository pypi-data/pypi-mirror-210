# -*- coding: utf-8 -*-
"""
Created on Tue Jan 20 15:00:00 2023

@author: yqlim
"""
import logging
logger = logging.getLogger(__name__)

import enum

@enum.unique
class ENUM_VOLATILITY_STICKINESS(enum.Enum):
    STRIKE = 1
    MONEYNESS = 2

@enum.unique
class ENUM_DAYCOUNT_CONVENTION(enum.Enum):
    ACT_360 = 'ACT/360'
    _30_360 = '30/360'
    ACT_250 = 'ACT/252'
    ACT_365 = 'ACT/365'
    _30_365 = '30/365'
    ACT_ACT = 'ACT/ACT'

@enum.unique
class ENUM_COMPOUNDING_FREQUENCY(enum.Enum):
    DISCRETE = 1
    CONTINUOUS = 2
    SIMPLE = 3  

@enum.unique
class ENUM_INTERPOLATION_METHOD(enum.Enum):
    LINEAR = 1
    CUBIC_SPLINE = 2

@enum.unique
class ENUM_EXTRAPOLATION_METHOD(enum.Enum):
    FLAT = 1