import logging
logger = logging.getLogger(__name__)

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import os
from dd8.connectivity.crypto import flipside_

if __name__ == '__main__':
    client = flipside_.FlipsideRest()
    data = client.query('67caa896-5989-4b57-96df-717349148f2e')
    print(data[0].keys())