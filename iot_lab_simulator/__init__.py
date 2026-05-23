"""
IoT Lab Simulator - A complete IoT experiments simulation suite
"""

__version__ = "1.0.0"
__author__ = "Shivaprasad"
__license__ = "MIT"

try:
    from .simulator import IoTLabSimulator, main
except ImportError:
    from iot_lab_simulator.simulator import IoTLabSimulator, main

__all__ = ['IoTLabSimulator', 'main']