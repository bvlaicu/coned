"""
ConEd calls the API of the ConEdison smart energy meter
to return the last meter read for a given meter number.
"""

from .meter import Meter
from .meter import MeterError

__version__ = '0.1.10'
