import logging
logger = logging.getLogger(__name__)

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dd8.connectivity.crypto import deribit_

if __name__ == '__main__':    
    key = os.getenv('DERIBIT_KEY')
    secret = os.getenv('DERIBIT_SECRET')
    print(key)
    print(secret)

    client = deribit_.DeribitWebsocket(api_key=os.getenv('DERIBIT_KEY'),
                                            api_secret=os.getenv('DERIBIT_SECRET'))
    # instruments = client.get_instruments(['ETH'], 'future', False)
    # print(instruments)
    #account_summary = client.get_account_summary('ETH')
    #print(account_summary)

    #book_summary = client.get_book_summary_by_currency('ETH', 'future')
    #print(book_summary)

    #delivery_prices = client.get_delivery_prices(['btc_usd', 'eth_usd'], 0, 10)
    #print(delivery_prices)

    #funding_data = client.get_funding_chart_data(['ETH-PERPETUAL'], '8h')
    #print(funding_data)

    # import datetime
    # end = datetime.datetime.now()
    # start = end - datetime.timedelta(days=5)
    # print(int(start.timestamp()*1000))
    # print(int(end.timestamp()*1000))
    # trades = client.get_last_trades_by_currency_and_time(['ETH'], int(start.timestamp()*1000), int(end.timestamp()*1000), 'option', 10, True)
    
    # print(trades)

    # trades = client.get_last_trades_by_currency(['BTC', 'ETH'], 'option', '', '', 10, True, 'default')
    # print(trades)

    # instrument_name = ['ETH-PERPETUAL', 'BTC-PERPETUAL']
    # order_book = client.get_order_book(instrument_name)
    # print(order_book)
    
    # client.subscribe_order_book('ETH-30DEC22-1300-P', group='none', depth=1)

    # option_chain = client.get_option_chain('ETH')
    # print(option_chain)

    index_price_names = client.get_index_price_names()
    print(index_price_names)