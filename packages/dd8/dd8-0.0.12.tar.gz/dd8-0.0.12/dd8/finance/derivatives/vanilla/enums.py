# -*- coding: utf-8 -*-
"""
Created on Tue Jan 20 15:00:00 2023

@author: yqlim
"""
import logging
logger = logging.getLogger(__name__)

import enum

@enum.unique
class ENUM_OPTION_TYPE(enum.Enum):
    PUT = 'p'
    CALL = 'c'

@enum.unique
class ENUM_OPTION_STYLE(enum.Enum):
    EUROPEAN = 'european'
    AMERICAN = 'american'
    PATH_DEPENDENT = 'path_dependent'

