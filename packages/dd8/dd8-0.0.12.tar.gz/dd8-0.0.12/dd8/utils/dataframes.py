# -*- coding: utf-8 -*-
"""
Created on Tue Dec 10 14:54:00 2021

@author: yqlim
"""
from typing import IO
from io import BytesIO, StringIO
import pandas as pd
import logging

logger = logging.getLogger(__name__)

def dataframe_to_bytes_buffer(dataframe: pd.DataFrame, file_name: str) -> IO:
    string_buff = StringIO()
    dataframe.to_csv(string_buff)
    bytes_buff = BytesIO()
    bytes_buff.write(string_buff.getvalue().encode())
    bytes_buff.seek(0)
    bytes_buff.name = file_name
