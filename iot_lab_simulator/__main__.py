"""Allow running the package as a module"""

import sys
import os

# Add parent directory to path if running directly
if __name__ == '__main__' and __package__ is None:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    __package__ = 'iot_lab_simulator'

# Now use relative import safely
from .simulator import main

if __name__ == '__main__':
    main()