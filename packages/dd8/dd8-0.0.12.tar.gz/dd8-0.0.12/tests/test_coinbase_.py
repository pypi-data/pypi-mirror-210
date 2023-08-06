import logging
logger = logging.getLogger(__name__)

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import os
from dd8.connectivity.crypto import coinbase_

if __name__ == '__main__':
    client = coinbase_.CoinbaseRest()
    # orderbook = client.get_order_book('ETH-USD')
    # print(orderbook)

    pairs = client.get_trading_pairs()
    print(pairs)