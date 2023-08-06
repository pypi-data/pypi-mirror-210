# -*- coding: utf-8 -*-
"""
Created on Tue Oct 18 22:15:00 2022

@author: yqlim
"""
from typing import Union, List
import numpy as np
import pandas as pd

from .enums import ENUM_MACHINE_LEARNING_TYPE

class Dataset(object):
    def __init__(self) -> None:
        pass

class TimeSeriesDataset(Dataset):
    # https://www.tensorflow.org/tutorials/structured_data/time_series
    # https://machinelearningmastery.com/using-cnn-for-financial-time-series-prediction/
    # https://stackoverflow.com/questions/42415076/how-to-insert-keras-model-into-scikit-learn-pipeline

    def __init__(self, data: pd.DataFrame, X_columns: Union[List[str], str], 
                    Y_columns: Union[List[str], str]) -> None:
        self.data = data
        self.X_columns = X_columns
        self.Y_columns = Y_columns

        self.n_samples = self.data.shape[0]
    
    def train_test_split(self, train_size: float, test_size: float, 
            validate_size: float) -> List[np.ndarray, np.ndarray, np.ndarray]:
        if not (train_size + test_size + validate_size) == 1.0:
            raise ValueError('sum of `train_size`, `test_size` and `validate_size` must equal 1.0.')

        train_count = int(train_size * self.n_samples)
        validate_count = int(validate_size * self.n_samples)
        
        train_idx = np.asarray(range(0, train_count, 1))
        validate_idx = np.asarray(range(train_count, validate_count, 1))
        test_idx = np.asarray(range(validate_count, self.n_samples, 1))

        return (train_idx, validate_idx, test_idx)

    @property
    def data(self) -> pd.DataFrame:
        return self.__df_data

    @data.setter
    def data(self, data: pd.DataFrame) -> None:
        if isinstance(data, pd.DataFrame):
            self.__df_data = data
        else:
            raise TypeError('`TimeSeriesDataset.data` must be of `pd.DataFrame` type.')
    
    @property
    def X_columns(self) -> List[str]:
        return self.__lst_X_columns
    
    @X_columns.setter
    def X_columns(self, X_columns: Union[List[str], str]) -> None:
        if isinstance(X_columns, (list, str)):
            X_columns = list(X_columns)
            if all(col in self.data.columns for col in X_columns):
                self.__lst_X_columns = X_columns
            else:
                raise ValueError('`TimeSeriesDataset.X_columns` contain header that does not exist in dataset.')
        else:
            raise TypeError('`TimeSeriesDataset.X_columns` must be of `list` or `str` type.')
        
    @property
    def Y_columns(self) -> List[str]:
        return self.__lst_Y_columns
    
    @Y_columns.setter
    def Y_columns(self, Y_columns: Union[List[str], str]) -> None:
        if isinstance(Y_columns, (list, str)):
            Y_columns = list(Y_columns)
            if all(col in self.data.columns for col in Y_columns):
                self.__lst_Y_columns = Y_columns
            else:
                raise ValueError('`TimeSeriesDataset.Y_columns` contain header that does not exist in dataset.')
        else:
            raise TypeError('`TimeSeriesDataset.Y_columns` must be of `list`or `str` type.')