import logging
logger = logging.getLogger(__name__)

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import os
from dd8.connectivity import binance_

if __name__ == '__main__':
    # client = binance_.BinanceWebsocket()
    # client.subscribe_order_book(print, 'btcusdt', 5)

    client = binance_.BinanceDataRest()
    data = client.get_historical_data('BTCUSDT', binance_.ENUM_RESOLUTION.MINUTE_15, '3 Mar 2022', '2 Mar 2023')
    print(data)
