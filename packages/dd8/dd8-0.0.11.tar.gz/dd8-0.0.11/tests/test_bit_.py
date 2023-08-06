import logging
logger = logging.getLogger(__name__)

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import os
from dd8.connectivity import bit_

if __name__ == '__main__':
    client = bit_.BitRest()
    indices = client.get_index(['USDT', 'BTC'])
    print(indices)