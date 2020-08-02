import numpy as np
import time
import sys, os

stuff = []
try:
    while True:
        stuff.append(np.ones(1024**2))
        time.sleep(1)
except KeyboardInterrupt:
    print("Saving state, exiting...")
    sys.exit(os.EX_SOFTWARE)
