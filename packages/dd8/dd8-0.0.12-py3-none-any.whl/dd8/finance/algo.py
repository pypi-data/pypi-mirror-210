# -*- coding: utf-8 -*-
"""
Created on Tue Oct 19 08:54:00 2022

@author: yqlim
"""
from typing import Union, List
from .data import MarketDataHistorical
from .technical_analysis import TechnicalIndicator

class Strategy(object):
    def __init__(self, indicators: Union[None, List[TechnicalIndicator]] = None) -> None:
        self.indicators = indicators

    def add_indicators(self, indicators: Union[None,List[TechnicalIndicator]]) -> None:
        if self.indicators:
            self.indicators += indicators
        else:
            self.indicators = indicators

    @property
    def indicators(self) -> Union[None, List[TechnicalIndicator]]:
        return self.__lst_indicators

    @indicators.setter
    def indicators(self, indicators: Union[None, List[TechnicalIndicator]]) -> None:
        checks = [isinstance(indicator, TechnicalIndicator) for indicator in indicators]
        assert (all(checks) or (indicators is None)), '`indicators` must a list of `TechnicalIndicator` objects.'
        self.indicators = indicators

class Portfolio(object):
    def __init__(self) -> None:
        pass

    def add_strategy(self, strategy: Strategy) -> None:
        pass

class Backtester(object):
    def __init__(self) -> None:
        self.data = None
        self.portfolio = None

    def set_data(self, data: Union[None, MarketDataHistorical]) -> None:
        pass

    def set_portfolio(self, portfolio: Union[None, Portfolio]) -> None:
        pass

    def test(self):
        pass
