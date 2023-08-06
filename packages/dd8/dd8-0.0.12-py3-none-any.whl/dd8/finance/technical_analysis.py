# -*- coding: utf-8 -*-
"""
Created on Tue Oct 11 15:23:00 2022

@author: yqlim
"""
import logging
logger = logging.getLogger(__name__)

from typing import Union, List, Tuple
import uuid
import pandas as pd
import numpy as np
from .enums import ENUM_RATE_OF_CHANGE_METHOD, ENUM_SMOOTHING_TYPE

def rolling_window(array1d: np.ndarray, window_size: int, stride: int) -> np.ndarray:
    """
    Generator yielding rolling windows to conserve memory.

    Parameters
    ----------
    array1d : np.ndarray
        initial array to generate rolling windows from
    window_size : int
        size of rolling window
    stride : int
        steps to generate rolling windows  (e.g. stride of 1 will have 
        `window_size`-1 overlapping elements with previous window)

    Yields
    ------
    np.ndarray
        one rolling window
    """
    N = len(array1d)
    for i in range(0, N-window_size+1, stride):
        yield array1d[i: i+window_size]    

class TechnicalIndicator(object):
    def __init__(self, uid: str = ''):
        self.uid = uid

    def fit(self, X: np.ndarray) -> np.ndarray:
        pass

    def target_level(self, target: float) -> float:
        pass

    @property
    def uid(self) -> str:
        return self.__str_uid
    
    @uid.setter
    def uid(self, uid: str) -> None:
        if uid:
            self.__str_uid = str(uid)
        else:
            self.__str_uid = uuid.uuid4()

    def _to_numpy_array(self, X: Union[pd.Series, np.ndarray]) -> np.ndarray:
        if not isinstance(X, np.ndarray):
            if isinstance(X, pd.Series):
                return X.values
            else:
                raise TypeError('`X` must be np.ndarray or pd.Series.')
        else:
            return X

class Label(TechnicalIndicator):
    def __init__(self, bins: List[Tuple[int, float]], uid: str = '') -> None:        
        super().__init__(uid)
        self.bins = bins
    
    @property
    def bins(self) -> List[Tuple[int, float]]:
        return self.__lst_bins

    @bins.setter
    def bins(self, bins: List[Tuple[int, float]]) -> None:
        self.__lst_bins = sorted(bins, key=lambda x: x[0])

    def fit(self, X: np.ndarray) -> np.ndarray:
        data = self._to_numpy_array(X).astype('float64')

        unique = np.unique(data)
        output = np.empty(len(data))
        output[:] = np.nan
        if len(unique) == len(self.bins):
            # discrete
            for label, value in self.bins:
                output[data==value] = label
        else:
            # continuous

            # labels, values = tuple(zip(*self.bins))
            # idx = np.digitize(X, values, right=False)
            # print(labels)
            # output[:] = np.asarray(labels)[idx]            
            
            for i in range(len(self.bins)-1):
                output[(~np.isnan(data)) & (data>=self.bins[i][1]) & (data<self.bins[i+1][1])] = self.bins[i+1][0]
            output[(~np.isnan(data)) & (data<self.bins[0][1])] = self.bins[0][0]
            output[(~np.isnan(data)) & (data>=self.bins[-1][1])] = self.bins[-1][0] + 1

        return output

class RateOfChange(TechnicalIndicator):
    def __init__(self, period: int, 
            method: ENUM_RATE_OF_CHANGE_METHOD = ENUM_RATE_OF_CHANGE_METHOD.NATURAL_LOG,
            shift: int = 0, uid: str = '') -> None:
        super().__init__(uid)
        self.period = period
        self.method = method
        self.shift = shift
        
    def fit(self, X: Union[pd.Series, np.ndarray], Y: Union[None, pd.Series, np.ndarray] = None) -> np.ndarray:
        data = self._to_numpy_array(X)
        if not Y is None:
            denominator = self._to_numpy_array(Y)
        else:
            denominator = data

        if self.method == ENUM_RATE_OF_CHANGE_METHOD.SIMPLE:
            rate_of_change = data[self.period : ] / denominator[ : -self.period] - 1.0
        elif self.method == ENUM_RATE_OF_CHANGE_METHOD.NATURAL_LOG:
            rate_of_change = np.log(data[self.period : ] / denominator[ : -self.period])
        if self.shift > 0:
            rate_of_change = rate_of_change[:-self.shift]
        padding = np.empty(self.period + self.shift)
        padding[:] = np.nan
        rate_of_change = np.concatenate([padding, rate_of_change], axis=0)
        
        return rate_of_change

    def target_level(self, target: float) -> float:
        pass

class RelativeStrengthIndex(TechnicalIndicator):
    def __init__(self, period: int, shift: int=0, uid: str = '') -> None:
        super().__init__(uid)
        self.period = period
        self.shift = shift

    def fit(self, X: Union[pd.Series, np.ndarray]) -> np.ndarray:
        data = self._to_numpy_array(X)                
        diff = np.diff(data)
        gains = np.abs(diff * (diff>0))
        losses = np.abs(diff * (diff<0)) 
        gains = (np.convolve(gains, np.ones(self.period), 'valid') / 
                     self.period)
        losses = (np.convolve(losses, np.ones(self.period), 'valid') / 
                      self.period)
        rsi = 100.0 - (100.0 / (1.0 + gains/losses))
        if self.shift > 0:
            rsi = rsi[:-self.shift]
        padding = np.empty(self.period + self.shift)
        padding[:] = np.nan
        rsi = np.concatenate([padding, rsi], axis=0)
        return rsi    
    
    def target_level(self, target: float) -> float:
        pass

class MovingAverage(TechnicalIndicator):
    def __init__(self, period: int, method: ENUM_SMOOTHING_TYPE = ENUM_SMOOTHING_TYPE.EXPONENTIAL_AVERAGING,
                    shift: int = 0, uid: str = ''):
        super().__init__(uid)
        self.period = period
        self.method = method
        self.shift = shift

    def fit(self, X: Union[pd.Series, np.ndarray]) -> np.ndarray:
        data = self._to_numpy_array(X)        
        result = []        
        if self.method == ENUM_SMOOTHING_TYPE.LINEAR_WEIGHTED_AVERAGING:
            windows = rolling_window(data, self.period, 1)
            for window in windows:
                result.append(np.mean(window))
        elif self.method == ENUM_SMOOTHING_TYPE.EXPONENTIAL_AVERAGING: 
            alpha = 2.0 / (self.period + 1.0)
            alpha_rev = 1-alpha
            n = data.shape[0]
            pows = alpha_rev**(np.arange(n+1))
            scale_arr = 1/pows[:-1]
            offset = data[0]*pows[1:]
            pw0 = alpha*alpha_rev**(n-1)

            mult = data*pw0*scale_arr
            cumsums = mult.cumsum()
            result = offset + cumsums*scale_arr[::-1]
            result = result[self.period-1:]

        result = np.asarray(result)
        if self.shift > 0:
            result = result[:-self.shift]        
        padding = np.empty(self.period - 1 + self.shift)
        padding[:] = np.nan
        result = np.concatenate([padding, result], axis=0)

        return result

    def target_level(self):
        pass

class StandardDeviation(TechnicalIndicator):
    def __init__(self, period: int, demean: bool = False, degrees_of_freedom: int = 1, 
                    smoothing_type: ENUM_SMOOTHING_TYPE = ENUM_SMOOTHING_TYPE.SIMPLE_AVERAGING,
                    periods_per_year: int = 0, shift: int = 0, uid: str = '') -> None:
        """
        Initialize an instance of the standard deviation technical indicator.

        Parameters
        ----------
        period : int
            number of periods used to compute standard deviation
        demean : bool, optional
            remove sample mean of each rolling window before computing
            standard deviation (default is True, which implies removal
            of sample mean as how standard deviation is usually computed)
        degrees_of_freedom : int, optional
            delta degrees of freedom, divisor used in calculation of 
            (N - degrees_of_freedom), where N represents number of elements
            (default is 1, which implies divisor of 1/(N-1) is used)
        smoothing_type : ENUM_SMOOTHING_TYPE, optional
            smoothing method used to compute sample mean when `demean` 
            parameter is set to `True` (default is `ENUM_SMOOTHING_TYPE.SIMPLE_AVERAGING`,
            which implies arithmetic averaging of values)
        periods_per_year : int, optional
            number of (trading) periods within a year, used for annualizing 
            computed parkinson volatility (default is 0, which implies
            that computed parkinson volatility will not be annualized)
        shift : int, optional
            number of shifts to apply to the computed parkinson volatility
            series (default is 0, which implies that the computed parkinson
            volatiity series is not shifted)
        uid : str
            unique identifier for this indicator (default is '', which
            implies `uuid.uuid4()`)
        """        
        super().__init__(uid)
        self.period = period
        self.demean = demean
        self.degrees_of_freedom = degrees_of_freedom
        self.smoothing_type = smoothing_type
        self.periods_per_year = periods_per_year
        self.shift = shift

    def fit(self, X: Union[pd.Series, np.ndarray]) -> np.ndarray:
        """
        Compute standard deviation for given data series.

        Parameters
        ----------
        X : pd.Series or np.ndarray
            data series to compute standard deviation for
        
        Return
        ------
        np.ndarray
            computed standard deviation series
        """        
        mean = 0        
        _ = self._to_numpy_array(X)
        result = []
        windows = rolling_window(_, self.period, 1)
        
        def _sigma(window, mean, period, degrees_of_freedom, periods_per_year):
            _ = np.sqrt(np.sum(np.square(window - mean)) / (self.period-self.degrees_of_freedom))
            if periods_per_year > 0:
                _ = _ * np.sqrt(periods_per_year)
            return _    

        def _mean(window):
            if self.smoothing_type == ENUM_SMOOTHING_TYPE.SIMPLE_AVERAGING:
                return np.average(window)
            else:
                raise NotImplementedError('`StandardDeviation.smoothing_type` not implemented.')        

        if self.demean:
            for window in windows:
                mean = _mean    (window)                
                result.append(
                    _sigma(window, mean, self.period, self.degrees_of_freedom, self.periods_per_year)
                )
        else:
            for window in windows:                                
                result.append(
                    _sigma(window, mean, self.period, self.degrees_of_freedom, self.periods_per_year)
                )
        
        result = np.asarray(result)
        if self.shift > 0:
            result = result[:-self.shift]        
        padding = np.empty(self.period - 1 + self.shift)
        padding[:] = np.nan
        result = np.concatenate([padding, result], axis=0)
        
        return result   

class ParkinsonVolatility(TechnicalIndicator):
    def __init__(self, period: int, periods_per_year: int = 0, 
                    shift: int = 0, uid: str = '') -> None:
        """
        Initialize an instance of the parkinson volatility technical indicator.

        Parameters
        ----------
        period : int
            number of periods used to compute the parkinson volatility
        periods_per_year : int, optional
            number of (trading) periods within a year, used for annualizing 
            computed parkinson volatility (default is 0, which implies
            that computed parkinson volatility will not be annualized)
        shift : int, optional
            number of shifts to apply to the computed parkinson volatility
            series (default is 0, which implies that the computed parkinson
            volatiity series is not shifted)
        uid : str
            unique identifier for this indicator (default is '', which
            implies `uuid.uuid4()`)
        """
        super().__init__(uid)
        self.period = period
        self.periods_per_year = periods_per_year
        self.shift = shift

    def fit(self, X: Union[pd.Series, np.ndarray]) -> np.ndarray:
        """
        Compute parkinson volatility for given intraday high-low
        return series (as computed by ln(high/low)).

        Parameters
        ----------
        X : pd.Series or np.ndarray
            ln(high/low) series to compute parkinson volatility for
        
        Return
        ------
        np.ndarray
            computed parkinson volatility series
        """
        _ = self._to_numpy_array(X)
        result = []
        windows = rolling_window(_, self.period, 1)
        for window in windows:
            vol = np.sqrt(np.sum(np.square(window)) * (1.0 / (4.0 * self.period * np.log(2.0))))
            if self.periods_per_year > 0:
                vol = vol * np.sqrt(self.periods_per_year)
            result.append(vol)

        result = np.asarray(result)
        if self.shift > 0:
            result = result[:-self.shift]        
        padding = np.empty(self.period - 1 + self.shift)
        padding[:] = np.nan
        result = np.concatenate([padding, result], axis=0)

        return result
