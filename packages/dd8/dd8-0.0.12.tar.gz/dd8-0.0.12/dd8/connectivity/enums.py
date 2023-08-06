# -*- coding: utf-8 -*-
"""
Created on Tue Sep 28 08:37:00 2022

@author: yqlim
"""

import enum

@enum.unique
class ENUM_SUPPORTED_EXCHANGES(enum.Enum):
    FTX = 1

@enum.unique
class ENUM_RESOLUTION(enum.Enum):
    #window length in seconds. options: 15, 60, 300, 900, 3600, 14400, 86400, 
    #or any multiple of 86400 up to 30*86400
    SECOND_1 = 1
    SECOND_15 = 15
    MINUTE_1 = 60
    MINUTE_3 = 180
    MINUTE_5 = 300
    MINUTE_15 = 900
    MINUTE_30 = 1800
    HOUR_1 = 3600
    HOUR_2 = 7200
    HOUR_4 = 14400
    HOUR_6 = 21600
    HOUR_8 = 28800
    HOUR_12 = 43200
    DAY_1 = 86400
    DAY_2 = (2*86400)
    DAY_3 = (3*86400)
    DAY_4 = (4*86400)
    DAY_5 = (5*86400)
    DAY_6 = (6*86400)
    DAY_7 = (7*86400)
    DAY_8 = (8*86400)
    DAY_9 = (9*86400)
    DAY_10 = (10*86400)
    DAY_11 = (11*86400)
    DAY_12 = (12*86400)
    DAY_13 = (13*86400)
    DAY_14 = (14*86400)
    DAY_15 = (15*86400)
    DAY_16 = (16*86400)
    DAY_17 = (17*86400)
    DAY_18 = (18*86400)
    DAY_19 = (19*86400)
    DAY_20 = (20*86400)
    DAY_21 = (21*86400)
    DAY_22 = (22*86400)
    DAY_23 = (23*86400)
    DAY_24 = (24*86400)
    DAY_25 = (25*86400)
    DAY_26 = (26*86400)
    DAY_27 = (27*86400)
    DAY_28 = (28*86400)
    DAY_29 = (29*86400)
    DAY_30 = (30*86400)