# -*- coding: utf-8 -*-
"""
Created on Tue Feb 23 18:00:00 2023

@author: yqlim
"""
import logging
logger = logging.getLogger(__name__)

from typing import Union
import numpy as np
import datetime
import uuid
from .enums import ENUM_VOLATILITY_STICKINESS

class VolatilitySurface(object):
    """
    Abstract Base Class to represent a volatility surface to be passed into a 
    `PricingModel`. 
        
    Parameters
    ----------
    strikes : np.ndarray
        matrix containing the strikes/moneyness of the volatility data,
        sorted chronologically by expiration, then in ascending order by
        strike/moneyness (e.g. [ [<lower_strike_tenor_1>, ..., <upper_strike_tenor_1>],
        [<lower_strike_tenor_2>, ..., <upper_strike_tenor_2>], ...])
    expirations : np.ndarrays
        array containing expiration datetime pillars of the volatility data
        (volatility term structure)
    surface : np.ndarray
        matrix containing the volatility data points - should have the same 
        dimension as the `strikes` matrix.
    stickiness : ENUM_VOLATILITY_STICKINESS, optional
        indicates meaning of values in the `strikes` matrix (default is 
        ENUM_VOLATILITY_STICKINESS.STRIKE, which implies values represent
        absolute strike levels of the options)
    reference_date : datetime.datetime, optional
        reference datetime of the volatility surface to allow for generation
        of historical pricing/valuation (default is None, which represents
        datetime.datetime.utcnow())
    surface_id : str, optional
        unique identifier (default is uuid.uuid4())
    
    Attributes
    ----------
    strikes
    expirations
    surface
    stickiness
    reference_date
    surface_id        
    """

    def __init__(self, strikes: np.ndarray, 
                    expirations: np.ndarray,
                    surface: np.ndarray,
                    stickiness: ENUM_VOLATILITY_STICKINESS = ENUM_VOLATILITY_STICKINESS.STRIKE,
                    reference_date: Union[datetime.datetime, None] = None,
                    surface_id: str = '') -> None:

        self.strikes = strikes
        self.expirations = expirations
        self.surface = surface
        self.stickiness = stickiness
        self.reference_date = reference_date
        self.surface_id = surface_id

    def __call__(self, strike: float, expiration: datetime.datetime) -> float:
        pass

    def get_volatility(self, strike: float, expiration: datetime.datetime) -> float:
        pass

    @property
    def strikes(self) -> np.ndarray:
        return self.__npa_strikes

    @strikes.setter
    def strikes(self, strikes: np.ndarray) -> None:
        if isinstance(strikes, np.ndarray):
            if strikes.dtype == np.floating:
                self.__npa_strikes = strikes
            else:
                raise TypeError('`VolatilitySurface.strikes` must be a matrix of `np.floating` type.')
        else:
            raise TypeError('`VolatilitySurface.strikes` must be of `np.ndarray` type.')

    @property
    def expirations(self) -> np.ndarray:
        return self.__npa_expirations

    @expirations.setter
    def expirations(self, expirations: np.ndarray) -> None:
        if isinstance(expirations, np.ndarray):
            self.__npa_expirations = expirations
        else:
            raise TypeError('`VolatilitySurface.expirations` muts be of `np.ndarray` type.')

    @property
    def surface(self) -> np.ndarray:
        return self.__npa_surface

    @surface.setter
    def surface(self, surface: np.ndarray) -> None:
        if isinstance(surface, np.ndarray):
            if surface.dtype == np.floating:
                self.__npa_surface = surface
            else:
                raise TypeError('`VolatilitySurface.surface` must be a matrix of `np.floating` type.')
        else:
            raise TypeError('`VolatilitySurface.surface` must be of `np.ndarray` type.')        

    @property
    def stickiness(self) -> ENUM_VOLATILITY_STICKINESS:
        return self.__enum_volatility_stickiness

    @stickiness.setter
    def stickiness(self, stickiness: ENUM_VOLATILITY_STICKINESS) -> None:
        if isinstance(stickiness, ENUM_VOLATILITY_STICKINESS):
            self.__enum_volatility_stickiness = stickiness
        else:
            raise TypeError('`VolatilitySurface.stickiness` must be of `ENUM_VOLATILITY_STICKINESS` type.')

    @property
    def reference_date(self) -> datetime.datetime:
        return self.__dte_reference_date

    @reference_date.setter
    def reference_date(self, reference_date: Union[datetime.datetime, None]) -> None:
        if isinstance(reference_date, datetime.datetime):
            if reference_date:
                self.__dte_reference_date = reference_date
            else:
                self.__dte_reference_date = datetime.datetime.utcnow()
        else:
            raise TypeError('`VolatilitySurface.reference_date` must be of `datetime.datetime` type.')
    
    @property
    def surface_id(self) -> str:
        return self.__str_surface_id

    @surface_id.setter
    def surface_id(self, surface_id: str) -> None:
        if not surface_id:
            self.__str_surface_id = str(uuid.uuid4())
        else:
            self.__str_surface_id = str(surface_id)

class Schedule(object):
    """
    Abstract Base Class to represent a schedule, where a numerical value, 
    such as interest rate or cashflow, is associated with a particular date. 
    
    Attributes
    ----------
    dates
    values
    uid 
    
    """
    def __init__(self, dates: np.ndarray, values: np.ndarray, schedule_id: str = ''):   
        """        
        Parameters
        ----------
        dates : np.ndarray
            numpy array containing `datetime.datetime` objects
        values : np.ndarray
            numpy array containing `np.floating` objects
        schedule_id : str, optional
            unique identifier (defualt is `uuid.uuid4()`)       
        """
        self.dates = dates
        self.values = values
        self.schedule_id = schedule_id

        self._check_dimension()
        self._sort_data()
        
    def _check_dimension(self) -> None:
        if not self.dates.ndim == 1:
            raise ValueError('`Schedule.dates` must be a 1-dimensional array.')
        if not self.values.ndim == 1:
            raise ValueError('`Schedule.values` must be a 1-dimensional array.')
        if not (self.dates.shape[0] == self.values.shape[0]):
            raise ValueError('`Schedule.dates` must be of equal length as `Schedule.values`.')
            
    def _sort_data(self) -> None:
        order = self.dates.argsort()
        self.dates = self.dates[order]
        self.values = self.values[order]
        
    @property
    def dates(self) -> np.ndarray:
        return self.__npa_dates
    
    @dates.setter
    def dates(self, dates: np.ndarray) -> None:
        if isinstance(dates, np.ndarray):
            self.__npa_dates = dates
        elif isinstance(dates, list):
            self.__npa_dates = np.array(dates)
        else:
            raise TypeError('`Schedule.dates` must be of `np.ndarray` type.')
        
    @property
    def values(self) -> np.ndarray:
        return self.__npa_values
    
    @values.setter
    def values(self, values) -> None:
        if isinstance(values, np.ndarray): 
            if values.dtype == np.floating:
                self.__npa_values = values
            else:
                raise TypeError('`Schedule.values` must be a matrix of `np.floating` type.')
        else:
            raise TypeError('`Schedule.values` must be of `np.ndarray` type.')
    
    @property
    def schedule_id(self) -> str:
        return self.__str_schedule_id
    
    @schedule_id.setter
    def schedule_id(self, schedule_id: str) -> None:
        if not schedule_id:
            self.__str_schedule_id = str(uuid.uuid4())
        else:
            self.__str_schedule_id = str(schedule_id)
        