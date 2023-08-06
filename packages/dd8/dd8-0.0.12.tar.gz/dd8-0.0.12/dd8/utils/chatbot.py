# -*- coding: utf-8 -*-
"""
Created on Tue Dec 10 14:54:00 2021

@author: yqlim
"""
from typing import Union, IO, Callable, Dict
import requests
import logging
# from telegram import Update
# from telegram.ext import Updater, CallbackContext, CommandHandler
from telegram.ext import Application, CommandHandler

logger = logging.getLogger(__name__)

class Telegram(object):
    _URL = r'https://api.telegram.org/bot{token}/'
    def __init__(self, token: str='', use_context: bool=True) -> None:
        self.token = token
        self.use_context = use_context
        # self.updater = Updater(self.token, self.use_context)
        # self.dispatcher = self.updater.dispatcher
        self.application = Application.builder().token(token).build()
    
    def _token_exists(self) -> bool:
        if not self.token:
            raise ValueError('no telegram token provided')
            return False        
        return True

    def poll(self, timeout: int=100000) -> None:
        # self.updater.start_polling(timeout=timeout)
        # self.updater.idle()
        self.application.run_polling(timeout=timeout)

    def add_command(self, command_name: str, command_func: Callable) -> None:
        handler = CommandHandler(command_name, command_func)
        self.application.add_handler(handler)
    
    def _send(self, url: str, params: Dict, files: Union[None, Dict]=None) -> None:
        if self._token_exists():
            requests.get(url, params=params)

    def send_message(self, chat_id: str, message: str) -> None:
        url = ''.join([self._URL, 'sendMessage']).format(token=self.token)
        params = {'chat_id' : chat_id, 'text' : message}
        self._send(url, params)

    def send_document(self, chat_id: str, file_name: str, document: IO) -> bool:
        url = ''.join([self._URL, 'sendDocument']).format(token=self.token)
        params = {'chat_id', chat_id}
        files = {'document' : (file_name, document)}
        self._send(url=url, params=params, files=files)