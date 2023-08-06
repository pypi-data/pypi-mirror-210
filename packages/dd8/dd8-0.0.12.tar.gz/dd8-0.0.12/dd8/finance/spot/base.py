# -*- coding: utf-8 -*-
"""
Created on Tue Mar 08 18:00:00 2023

@author: yqlim
"""
import logging
logger = logging.getLogger(__name__)

class Underlying(object):
    def __init__(self, symbol: str) -> None:
        self.symbol = symbol

    def __str__(self) -> str:
        return 'Underlying({symbol})'.format(symbol=self.symbol)

    def __repr__(self) -> str:
        return 'Underlying({symbol})'.format(symbol=self.symbol)

    def __lt__(self, to_compare: 'Underlying') -> bool:
        return self.symbol < to_compare.symbol
    
    def __le__(self, to_compare: 'Underlying') -> bool:
        return self.symbol <= to_compare.symbol

    def __gt__(self, to_compare: 'Underlying') -> bool:
        return self.symbol > to_compare.symbol

    def __ge__(self, to_compare: 'Underlying') -> bool:
        return self.symbol >= to_compare.symbol

    def __eq__(self, to_compare: 'Underlying') -> bool:
        return self.symbol == to_compare.symbol

    def __ne__(self, to_compare: 'Underlying') -> bool:
        return self.symbol != to_compare.symbol                    

    @property
    def symbol(self) -> str:
        return self.__str_symbol
    
    @symbol.setter
    def symbol(self, symbol: str) -> None:
        self.__str_symbol = str(symbol).strip().upper()
    
