# -*- coding: utf-8 -*-
"""
Created on Tue Mar 08 18:00:00 2023

@author: yqlim
"""
import logging
logger = logging.getLogger(__name__)

from .base import Underlying

class Security(Underlying):
    def __init__(self) -> None:
        pass

class Cryptocurrency(Underlying):
    def __init__(self, quote_currency: str, base_currency: str = 'USD') -> None:
        super().__init__(quote_currency)        
        self.base_currency = base_currency

    def __str__(self) -> str:
        return 'Cryptocurrency({quote_currency}, {base_currency})'.format(
            quote_currency=self.quote_currency,
            base_currency=self.base_currency
        )

    def __repr__(self) -> str:
        return 'Cryptocurrency({quote_currency}, {base_currency})'.format(
            quote_currency=self.quote_currency,
            base_currency=self.base_currency
        )

    @property
    def quote_currency(self) -> str:
        return self.symbol

    @quote_currency.setter
    def quote_currency(self, quote_currency) -> None:
        self.symbol = quote_currency.strip().upper()

    @property
    def base_currency(self) -> str:
        return self.__str_base_currency
    
    @base_currency.setter
    def base_currency(self, base_currency: str) -> None:
        self.__str_base_currency = base_currency.strip().upper()