import logging
logger = logging.getLogger(__name__)

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import os
from dd8.connectivity.crypto import talos_

if __name__ == '__main__':
    client = talos_.TalosRest()
