# -*- coding: utf-8 -*-
"""
Created on Tue Oct 10 14:54:00 2022

@author: yqlim
"""

from typing import Union
import numpy as np
import pandas as pd

class MarketDataHistorical(object):
    """
    A standardized format for OHLCV historical market data. Data is sorted by
    timestamp, with index 0 representing the oldest data point and index -1
    representing the latest data point.

    Parmeters
    ---------
    data : np.ndarray, optional
        ohlcv market data with `timestamp` and `source` data - timestamp is Unix
        timestamp in milliseconds (the default is `None`)
    """
    def __init__(self, source: str, data: Union[None, np.ndarray] = None) -> None:
        self.columns = {'timestamp' : 0, 'open' : 1, 'high' : 2,
                        'low' : 3, 'close' : 4, 'volume' : 5}
        self.data = data
        
    def __add__(self, data: 'MarketDataHistorical') -> 'MarketDataHistorical':
        _ = np.vstack((self.data, data))
        _ = _[_[:, self.columns['timestamp']].argsort()]

    def _slice(self, header: str, idx_start: int, idx_end: int) -> Union[None, np.ndarray]:
        if not self.data is None:
            if idx_start == -99 and idx_end == -99:
                return self.data[:, self.columns[header]]
            elif idx_start == -99:
                return self.data[:idx_end, self.columns[header]]
            elif idx_end == -99:
                return self.data[idx_start:, self.columns[header]]
            else:
                return self.data[idx_start: idx_end, self.columns[header]]
        else:
            return None        

    @property
    def data(self) -> np.ndarray:
        return self.__nda_data

    @data.setter
    def data(self, data: np.ndarray) -> None:
        assert isinstance(data, np.ndarray), '`MarketDataHistorical.data` needs to be of `np.ndarray` type.'
        assert len(self.columns) == len(data[0]), '`MarketDataHistorical.data` must have `timestamp`, `open`, \
            `high`, `low`, `close`, `volume`, `source` columns.'
        self.__nda_data = data[data[:, self.columns['timestamp']].argsort()]

    def extend(self, header: str, data: np.ndarray) -> None:
        assert self.data.shape[0] == len(data), 'new feature must have same number of rows.'
        self.columns[header] = self.data.shape[1]    
        self.data = np.hstack((self.data, data[:, np.newaxis]))        

    def to_csv(self, filepath: str, timestamp_as_datetime: bool = True) -> None:
        """
        Output data to csv.

        Parameters
        ----------
        filepath : str
            full filepath (with file extension) to output data
        timestamp_as_datetime : bool, optional
            convert timestamp column(s) to human-readable datetime format (DD MMM YYYY HH:MM:SS)
            (the default is True, which implies timestamp will be converted to human-readable format)
        """
        _ = pd.DataFrame(self.data, columns=self.columns)
        if timestamp_as_datetime:
            _.loc[:, 'timestamp'] = pd.to_datetime(_.loc[:, 'timestamp'], unit='ms').dt.strftime('%d %b %Y %H:%M:%S')
        _.to_csv(filepath, index=False)

    def timestamp(self, idx_start: int = -99, idx_end: int = -99) -> Union[None, np.ndarray]:
        """
        Slice timestamp column.

        Parameters
        ----------
        idx_start : int, optional
            index of oldest timestamp to start slicing, inclusive (the default is -99,
            which implies slicing from the oldest timestamp)

        idx_end : int, optional
            index of latest timestamp to end slicing, exclusive (the default is -99,
            which implies slicing to the latest timestamp)

        Return
        ------
        np.ndarray
            a slice of timestamp column

        """
        return self._slice('timestamp', idx_start, idx_end).astype('int64')

    def open(self, idx_start: int = -99, idx_end: int = -99) -> Union[None, np.ndarray]:
        """
        Slice open prices column.

        Parameters
        ----------
        idx_start : int, optional
            index of oldest timestamp to start slicing, inclusive (the default is -99,
            which implies slicing from the oldest timestamp)

        idx_end : int, optional
            index of latest timestamp to end slicing, exclusive (the default is -99,
            which implies slicing to the latest timestamp)

        Return
        ------
        np.ndarray
            a slice of open prices column

        """
        return self._slice('open', idx_start, idx_end).astype('float64')

    def high(self, idx_start: int = -99, idx_end: int = -99) -> Union[None, np.ndarray]:
        """
        Slice high prices column.

        Parameters
        ----------
        idx_start : int
            index of oldest timestamp to start slicing, inclusive (the default is -99,
            which implies slicing from the oldest timestamp)

        idx_end : int, optional
            index of latest timestamp to end slicing, exclusive (the default is -99,
            which implies slicing to the latest timestamp)

        Return
        ------
        np.ndarray
            a slice of high prices column

        """
        return self._slice('high', idx_start, idx_end)

    def low(self, idx_start: int = -99, idx_end: int = -99) -> Union[None, np.ndarray]:
        """
        Slice low prices column.

        Parameters
        ----------
        idx_start : int
            index of oldest timestamp to start slicing, inclusive (the default is -99,
            which implies slicing from the oldest timestamp)

        idx_end : int, optional
            index of latest timestamp to end slicing, exclusive (the default is -99,
            which implies slicing to the latest timestamp)

        Return
        ------
        np.ndarray
            a slice of low prices column

        """
        return self._slice('low', idx_start, idx_end).astype('float64')

    def close(self, idx_start: int = -99, idx_end: int = -99) -> Union[None, np.ndarray]:
        """
        Slice close prices column.

        Parameters
        ----------
        idx_start : int
            index of oldest timestamp to start slicing, inclusive (the default is -99,
            which implies slicing from the oldest timestamp)

        idx_end : int, optional
            index of latest timestamp to end slicing, exclusive (the default is -99,
            which implies slicing to the latest timestamp)

        Return
        ------
        np.ndarray
            a slice of close prices column

        """
        return self._slice('close', idx_start, idx_end).astype('float64')

    def volume(self, idx_start: int = -99, idx_end: int = -99) -> Union[None, np.ndarray]:
        """
        Slice volumes column.

        Parameters
        ----------
        idx_start : int
            index of oldest timestamp to start slicing, inclusive (the default is -99,
            which implies slicing from the oldest timestamp)

        idx_end : int, optional
            index of latest timestamp to end slicing, exclusive (the default is -99,
            which implies slicing to the latest timestamp)

        Return
        ------
        np.ndarray
            a slice of volumes column

        """
        return self._slice('volume', idx_start, idx_end).astype('float64')