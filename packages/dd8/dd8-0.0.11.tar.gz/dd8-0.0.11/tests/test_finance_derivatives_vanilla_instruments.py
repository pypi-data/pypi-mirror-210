import logging
logger = logging.getLogger(__name__)

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dateutil import parser
import dd8.finance.derivatives.vanilla.instruments as vanilla
import dd8.finance.spot.instruments as spot

if __name__ == '__main__':
    # Testing sorting functionality of `dd8.finance.derivatives.vanilla.instruments.OptionCrypto` class

    options = [
        vanilla.OptionCrypto(parser.parse('31 Mar 2023 08:00'), 20000.0, vanilla.ENUM_OPTION_TYPE.PUT, vanilla.ENUM_OPTION_STYLE.EUROPEAN,spot.Cryptocurrency('BTC')),
        vanilla.OptionCrypto(parser.parse('31 Mar 2023 08:00'), 19000.0, vanilla.ENUM_OPTION_TYPE.PUT, vanilla.ENUM_OPTION_STYLE.EUROPEAN,spot.Cryptocurrency('BTC')),
        vanilla.OptionCrypto(parser.parse('30 Jun 2023 08:00'), 20000.0, vanilla.ENUM_OPTION_TYPE.PUT, vanilla.ENUM_OPTION_STYLE.EUROPEAN,spot.Cryptocurrency('BTC')),
        vanilla.OptionCrypto(parser.parse('30 Jun 2023 08:00'), 19500.0, vanilla.ENUM_OPTION_TYPE.PUT, vanilla.ENUM_OPTION_STYLE.EUROPEAN,spot.Cryptocurrency('BTC')),
        vanilla.OptionCrypto(parser.parse('31 Mar 2023 08:00'), 20000.0, vanilla.ENUM_OPTION_TYPE.PUT, vanilla.ENUM_OPTION_STYLE.AMERICAN,spot.Cryptocurrency('BTC')),
        vanilla.OptionCrypto(parser.parse('31 Mar 2023 08:00'), 19000.0, vanilla.ENUM_OPTION_TYPE.PUT, vanilla.ENUM_OPTION_STYLE.AMERICAN,spot.Cryptocurrency('BTC')),
        vanilla.OptionCrypto(parser.parse('30 Jun 2023 08:00'), 20000.0, vanilla.ENUM_OPTION_TYPE.PUT, vanilla.ENUM_OPTION_STYLE.AMERICAN,spot.Cryptocurrency('BTC')),
        vanilla.OptionCrypto(parser.parse('30 Jun 2023 08:00'), 19500.0, vanilla.ENUM_OPTION_TYPE.PUT, vanilla.ENUM_OPTION_STYLE.AMERICAN,spot.Cryptocurrency('BTC')),
        vanilla.OptionCrypto(parser.parse('31 Mar 2023 08:00'), 20000.0, vanilla.ENUM_OPTION_TYPE.CALL, vanilla.ENUM_OPTION_STYLE.EUROPEAN,spot.Cryptocurrency('BTC')),
        vanilla.OptionCrypto(parser.parse('31 Mar 2023 08:00'), 19000.0, vanilla.ENUM_OPTION_TYPE.CALL, vanilla.ENUM_OPTION_STYLE.EUROPEAN,spot.Cryptocurrency('BTC')),
        vanilla.OptionCrypto(parser.parse('30 Jun 2023 08:00'), 20000.0, vanilla.ENUM_OPTION_TYPE.CALL, vanilla.ENUM_OPTION_STYLE.EUROPEAN,spot.Cryptocurrency('BTC')),
        vanilla.OptionCrypto(parser.parse('30 Jun 2023 08:00'), 19500.0, vanilla.ENUM_OPTION_TYPE.CALL, vanilla.ENUM_OPTION_STYLE.EUROPEAN,spot.Cryptocurrency('BTC')),
        vanilla.OptionCrypto(parser.parse('31 Mar 2023 08:00'), 20000.0, vanilla.ENUM_OPTION_TYPE.CALL, vanilla.ENUM_OPTION_STYLE.AMERICAN,spot.Cryptocurrency('BTC')),
        vanilla.OptionCrypto(parser.parse('31 Mar 2023 08:00'), 19000.0, vanilla.ENUM_OPTION_TYPE.CALL, vanilla.ENUM_OPTION_STYLE.AMERICAN,spot.Cryptocurrency('BTC')),
        vanilla.OptionCrypto(parser.parse('30 Jun 2023 08:00'), 20000.0, vanilla.ENUM_OPTION_TYPE.CALL, vanilla.ENUM_OPTION_STYLE.AMERICAN,spot.Cryptocurrency('BTC')),
        vanilla.OptionCrypto(parser.parse('30 Jun 2023 08:00'), 19500.0, vanilla.ENUM_OPTION_TYPE.CALL, vanilla.ENUM_OPTION_STYLE.AMERICAN,spot.Cryptocurrency('BTC')),
    ]

    print(sorted(options, reverse=True))