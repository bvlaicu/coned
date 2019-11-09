"""Main test class for coned"""

from coned import Meter
from coned import MeterError
import pytest


def test_get_last_meter_read():
    meter = Meter("9608064")
    read = meter.last_read()
    assert isinstance(read, float)


def test_invalid_meter():
    with pytest.raises(MeterError) as err:
        meter = Meter("invalid_meter_number")
        read = meter.last_read()
    assert err is not None
