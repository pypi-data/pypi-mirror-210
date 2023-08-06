__version__ = "1.0.6"

# Import required libraries
import numpy as np
import serial
import serial.tools.list_ports
import time

# Import main functions
from syncmaster.device import SyncMaster
from syncmaster.analysis import getEvents
