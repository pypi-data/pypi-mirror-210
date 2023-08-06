# -*- coding: utf-8 -*-
"""
Created on Tue Jan 17 12:52:00 2023

@author: yqlim
"""
import logging
logger = logging.getLogger(__name__)

import uuid

class RequestForQuote(object):
    def __init__(self, requestor: str = '', request_id: str = '') -> None:
        self.requestor = requestor
        if request_id:
            self.request_id = request_id
        else:
            self.request_id = uuid.uuid4()

class Order(object):
    def __init__(self, symbol: str = '', quantity: float = 0.0, 
                    price: float = 0.0, order_id: str = '') -> None:
        self.symbol = symbol        
        self.quantity = quantity
        self.price = price

        self.order_id = order_id

    @property
    def symbol(self) -> str:
        return self.__str_symbol

    @symbol.setter
    def symbol(self, symbol: str) -> None:
        if isinstance(symbol, str): 
            if symbol:            
                self.__str_symbol = symbol
            else:
                raise ValueError('invalid `Order.symbol`.')
        else:
            raise TypeError('`Order.symbol` must be of `str` type.')
    
    @property
    def quantity(self) -> float:
        return self.__dbl_quantity
    
    @quantity.setter
    def quantity(self, quantity: float) -> None:
        if isinstance(quantity, float):
            self.__dbl_quantity = quantity
        else:
            raise TypeError('`Order.quantity` must be of `float` type.')
    
    @property
    def price(self) -> float:
        return self.__dbl_price

    @price.setter
    def price(self, price: float) -> None:
        if isinstance(price, float):
            self.__dbl_price = price
        else:
            raise TypeError('`Order.price` must be of `float` type.')

    @property
    def order_id(self) -> str:
        return self.__str_order_id
    
    @order_id.setter
    def order_id(self, order_id: str) -> None:
        if order_id:
            self.__str_order_id = str(order_id)
        else:
            self.__str_order_id = uuid.uuid4()