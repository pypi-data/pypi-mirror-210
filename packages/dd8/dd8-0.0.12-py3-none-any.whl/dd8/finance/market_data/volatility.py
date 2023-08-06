# -*- coding: utf-8 -*-
"""
Created on Tue Feb 23 18:00:00 2023

@author: yqlim
"""
import logging
logger = logging.getLogger(__name__)

from collections import OrderedDict
import datetime
import numpy as np

from .base import VolatilitySurface

class VolatilitySurfaceConstant(VolatilitySurface):
    """
    Inheriting from `VolatilitySurface` base class to return a constant volatility
    regardless of option strike or expiration. 
        
    Parameters
    ----------
    constant_volatility : float
        constant volatility to return regardless of option strike or expiration
    
    Attributes
    ----------
    strikes
    expirations
    surface
    stickiness
    reference_date
    surface_id      
    constant_volatility  
    """    
    def __init__(self, constant_volatility: float) -> None:
        super().__init__(np.array([[]]), np.array([]), np.array([[]]))
        self.constant_volatility = constant_volatility
    
    def __call__(self, strike: float, expiration: datetime.datetime) -> float:
        return self.constant_volatility

    def get_volatility(self, strike: float, expiration: datetime.datetime) -> float:
        return self.constant_volatility

    @property
    def constant_volatility(self) -> float:
        return self.__dbl_constant_volatility

    @constant_volatility.setter
    def constant_volatility(self, constant_volatility: float) -> None:
        if isinstance(constant_volatility, float):
            if constant_volatility >= 0.0:
                self.constant_volatility = constant_volatility
            else:
                raise ValueError('`VolatilitySurfaceConstant.constant_volatility` must be non-negative.')
        else:
            raise TypeError('`VolatilitySurfaceConstant.constant_volatility` must be of `float` type.')






