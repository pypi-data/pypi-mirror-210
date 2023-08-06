# -*- coding: utf-8 -*-
"""
Created on Tue Oct 21 22:15:00 2022

@author: yqlim
"""
from typing import Union, List
import numpy as np

class Arima(object):
    def __init__(self) -> None:
        pass

class WindowGenerator(object):
    def __init__(self, input_width: int, label_width: int, shift: int,
                    label_columns: Union[None, List[str]]=None):
        self.input_width = input_width
        self.label_width = label_width
        self.shift = shift
        self.label_columns = label_columns

        if not label_columns is None:
            self.label_columns_idx = {name : i for i, name in enumerate(self.label_columns)}
        
        self.total_window_size = self.input_width + self.shift
        self.input_slice = slice(0, self.input_width)
        self.input_idx = np.arange(self.total_window_size)[self.input_slice]

        self.label_start = self.total_window_size - self.label_width
        self.labels_slice = slice(self.label_start, None)
        self.label_idx = np.arange(self.total_window_size)[self.labels_slice]

    def __str__(self):
        return '\n'.join([
            'Total window size: {total_window_size}'.format(total_window_size=self.total_window_size),
            'Input indices: {input_idx}'.format(input_idx=self.input_idx),
            'Label indices: {label_idx}'.format(label_idx=self.label_idx),
            'Label column name(s): {label_columns}'.format(label_columns=self.label_columns)   
        ])

if __name__ == '__main__':
    window = WindowGenerator(input_width=6, label_width=1, shift=1)
    print(window)