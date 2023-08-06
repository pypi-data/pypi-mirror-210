# -*- coding: utf-8 -*-
"""
Created on Fri Oct 14 21:36:24 2022

@author: LIM YUAN QING
"""
import logging
logger = logging.getLogger(__name__)

import os
from typing import Union, List, Dict
import enum
import pandas as pd
import numpy as np
import datetime

@enum.unique
class ENUM_COMPARISON_OPERATOR(enum.Enum):
    EQUAL = r'{df}.loc[{df}.loc[:, {field}]=={value_1}, :]'
    NOT_EQUAL = r'{df}.loc[{df}.loc[:, {field}]!={value_1}, :]'
    BETWEEN = r'{df}.loc[({df}.loc[:, {field}]>={value_1}) & ({df}.loc[:, {field}]<{value_2}), :]'
    GREATER = r'{df}.loc[{df}.loc[:, {field}]>{value_1}, :]'
    GREATER_EQUAL = r'{df}.loc[{df}.loc[:, {field}]>={value_1}, :]'
    LESSER = r'{df}.loc[{df}.loc[:, {field}]<{value_1}, :]'
    LESSER_EQUAL = r'{df}.loc[{df}.loc[:, {field}]<={value_1}, :]'

class Condition(object):
    def __init__(self, field: str, operator: ENUM_COMPARISON_OPERATOR,
                     value_1: float, value_2: float = None) -> None:
        self.field = field
        self.operator = operator
        self.value_1 = value_1
        self.value_2 = value_2
    
    def apply_to(self, data: pd.DataFrame) -> pd.DataFrame:
        if self.field in data.columns:
            string_to_evaluate = self.operator.value.format(df='data', 
                                                            field='"' + self.field + '"',
                                                            value_1=self.value_1)
            if not self.value_2 is None:
                string_to_evaluate = self.operator.value.format(value_2=self.value_2)
            
            print(string_to_evaluate)            
            return eval(string_to_evaluate)
        else:
            return data

class BacktestResult(object):
    _DEFAULT_COLUMNS = ['Pass', 'Result', 'Profit', 'Expected Payoff', 
                        'Profit Factor', 'Recovery Factor', 'Sharpe Ratio', 
                        'Custom', 'Equity DD %', 'Trades']
    def __init__(self) -> None:
        self.data = None
        self.conditions = []
    
    def from_csv(self, filepath: str) -> None:
        self.data = pd.read_csv(filepath)
        
    def from_xml(self, filepath: str) -> None:
        self.data = pd.read_xml(filepath)

    def add_filter_condition(self, condition: Condition) -> None:
        if isinstance(condition, Condition):
            self.conditions.append(condition)
            
    def filter_results(self) -> pd.DataFrame:
        if (not self.data is None) and (not self.conditions is None):
            for condition in self.conditions:
                self.data = condition.apply_to(self.data)
            
    def prioritize(self, priorities: Dict) -> None:
        if not self.data is None:
            self.data.sort_values(by=list(priorities.keys()), 
                                      ascending=list(priorities.values()))

    def combine(self, filepath: str, output_suffix: str = '') -> None:
        with open(filepath, 'r') as f:
            template = f.readlines()
            
        template = '\n'.join(template)
        output = ''
        params = self.data.drop(self._DEFAULT_COLUMNS, axis=1, inplace=False)
        data = params.values.astype(str)
        columns = params.columns[np.newaxis, :]
        data = (columns + ' = ' + data).tolist()
        
        for row in data:
            output += template.replace('{repeat}', ';'.join(row) + ';')
        
        directory, filename = os.path.split(filepath)
        _ = filename.split('.')
        filename = '_'.join([_[0], 'combined', datetime.datetime.now().strftime('%Y%m%d'), output_suffix]) + '.' + _[1]
        
        with open(os.path.join(directory, filename), 'w') as f:
            f.write(output)        
        
        return output

    @property
    def data(self) -> pd.DataFrame:
        return self.__df_data
    
    @data.setter
    def data(self, data: pd.DataFrame) -> None:
        if isinstance(data, pd.DataFrame):
            self.__df_data = data
            self.__df_data.loc[self.__df_data.loc[:, 'Profit Factor']==0, 'Profit Factor'] = 999

    @property
    def parameters(self) -> Union[List, None]:
        if not self.data is None:
            columns = self.data.columns
            params = [header for header in columns if header not in self._DEFAULT_COLUMNS]
            return params
        else:
            return None


