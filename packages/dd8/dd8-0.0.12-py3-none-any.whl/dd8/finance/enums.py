# -*- coding: utf-8 -*-
"""
Created on Tue Oct 10 14:54:00 2022

@author: yqlim
"""
import enum

@enum.unique
class ENUM_RATE_OF_CHANGE_METHOD(enum.Enum):
    SIMPLE = 1
    NATURAL_LOG = 2

@enum.unique
class ENUM_EXCHANGE(enum.Enum):
    FTX = 1
    DERIBIT = 2
    COINBASE = 3

@enum.unique
class ENUM_SMOOTHING_TYPE(enum.Enum):
    NONE = 1
    SIMPLE_AVERAGING = 2
    EXPONENTIAL_AVERAGING = 3
    SMOOTHED_AVERAGING = 4
    LINEAR_WEIGHTED_AVERAGING = 5