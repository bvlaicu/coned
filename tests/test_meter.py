"""Main test class for meter"""

from coned import Meter
from coned import MeterError
import pytest
import asyncio
import os

@pytest.fixture
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()

def test_get_last_meter_read(event_loop):
    meter = Meter(
        email=os.getenv("EMAIL"),
        password=os.getenv("PASSWORD"),
        mfa_type=os.getenv("MFA_TYPE"),
        mfa_secret=os.getenv("MFA_SECRET"),
        account_uuid=os.getenv("ACCOUNT_UUID"),
        meter_number=os.getenv("METER_NUMBER"),
        site=os.getenv("SITE"),
        # browser_path="/Users/bvlaicu/Library/Application Support/pyppeteer/local-chromium/588429/chrome-mac/Chromium.app/Contents/MacOS/Chromium"
    )
    startTime, endTime, val, uom = event_loop.run_until_complete(meter.last_read())
    assert isinstance(val, float)

# def test_invalid_meter(event_loop):
#     with pytest.raises(MeterError) as err:
#         meter = Meter(
#             email=os.getenv("INVALID_EMAIL"),
#             password=os.getenv("INVALID_PASSWORD"),
#             mfa_type=os.getenv("INVALID_MFA_TYPE"),
#             mfa_secret=os.getenv("INVALID_MFA_SECRET"),
#             account_uuid=os.getenv("INVALID_ACCOUNT_UUID"),
#             meter_number=os.getenv("INVALID_METER_NUMBER"))
#         val, uom = event_loop.run_until_complete(meter.last_read())
#     assert err is not None
