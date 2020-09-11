"""ConEdison or Orange and Rockland Utility Smart Energy Meter"""
import requests
import logging
import asyncio
from pyppeteer import launch
import os
import json
import pyotp

_LOGGER = logging.getLogger(__name__)


class MeterError(Exception):
    pass


class Meter(object):
    """A smart energy meter of ConEdison or Orange and Rockland Utility.

    Attributes:
        email: A string representing the email address of the account
        password: A string representing the password of the account
        mfa_type: Meter.MFA_TYPE_SECURITY_QUESTION or Meter.MFA_TYPE_TOTP
        mfa_secret: A string representing the multiple factor authorization secret
        account_uuid: A string representing the account uuid
        meter_number: A string representing the meter number
        site: Optional. Either `coned` (default, for ConEdison) or `oru` (for Orange and Rockland Utility)
        loop: Optional. Specific event loop if needed. Defaults to creating the event loop.
        browser_path: Optional. Specific chromium browser installation. Default to the installation that comes with pyppeteer.
    """

    MFA_TYPE_SECURITY_QUESTION = 'SECURITY_QUESTION'
    MFA_TYPE_TOTP = 'TOTP'
    SITE_CONED = 'coned'
    SITE_ORU = 'oru'

    def __init__(self, email, password, mfa_type, mfa_secret, account_uuid, meter_number, site='coned', loop=None, browser_path=None):
        """Return a meter object whose meter id is *meter_number*"""
        self.email = email
        if self.email is None:
            raise MeterError("Error initializing meter data - email is missing")
        # _LOGGER.debug("email = %s", self.email.replace(self.email[:10], '*'))

        self.password = password
        if self.password is None:
            raise MeterError("Error initializing meter data - password is missing")
        # _LOGGER.debug("password = %s", self.password.replace(self.password[:9], '*'))

        self.mfa_type = mfa_type
        if self.mfa_type is None:
            raise MeterError("Error initializing meter data - mfa_type is missing")
        _LOGGER.debug("mfa_type = %s", self.mfa_type)
        if self.mfa_type not in [Meter.MFA_TYPE_SECURITY_QUESTION, Meter.MFA_TYPE_TOTP]:
            raise MeterError("Error initializing meter data - unsupported mfa_type %s", self.mfa_type)

        self.mfa_secret = mfa_secret
        if self.mfa_secret is None:
            raise MeterError("Error initializing meter data - mfa_secret is missing")
        # _LOGGER.debug("mfa_secret = %s", self.mfa_secret.replace(self.mfa_secret[:8], '*'))

        self.account_uuid = account_uuid
        if self.account_uuid is None:
            raise MeterError("Error initializing meter data - account_uuid is missing")
        # _LOGGER.debug("account_uuid = %s", self.account_uuid.replace(self.account_uuid[:20], '*'))

        self.meter_number = meter_number
        if self.meter_number is None:
            raise MeterError("Error initializing meter data - meter_number is missing")
        # _LOGGER.debug("meter_number = %s", self.meter_number.replace(self.meter_number[:5], '*'))

        self.site = site
        _LOGGER.debug("site = %s", self.site)
        if self.site not in [Meter.SITE_CONED, Meter.SITE_ORU]:
            raise MeterError("Error initializing meter data - unsupported site %s", self.site)

        self.loop = loop
        _LOGGER.debug("loop = %s", self.loop)

        self.browser_path = browser_path
        _LOGGER.debug("browser_path = %s", self.browser_path)

    async def last_read(self):
        """Return the last meter read value and unit of measurement"""
        try:
            asyncio.set_event_loop(self.loop)
            asyncio.get_event_loop().create_task(self.browse())
            await self.browse()

            # parse the return reads and extract the most recent one
            # (i.e. last not None)
            jsonResponse = json.loads(self.raw_data)
            lastRead = None
            for read in jsonResponse['reads']:
                if read['value'] is None:
                    break
                lastRead = read
            _LOGGER.debug("lastRead = %s", lastRead)

            self.startTime = lastRead['startTime']
            self.endTime = lastRead['endTime']
            self.last_read_val = lastRead['value']
            self.unit_of_measurement = jsonResponse['unit']

            _LOGGER.debug("last read = %s %s %s %s", self.startTime, self.endTime, self.last_read_val, self.unit_of_measurement)

            return self.startTime, self.endTime, self.last_read_val, self.unit_of_measurement
        except:
            raise MeterError("Error requesting meter data")

    async def browse(self):
        browser_launch_config = {
            "defaultViewport": {"width": 1920, "height": 1080},
            "dumpio": True,
            "args": ["--no-sandbox"]}
        if self.browser_path is not None:
            browser_launch_config['executablePath'] = self.browser_path
        _LOGGER.debug("browser_launch_config = %s", browser_launch_config)

        browser = await launch(browser_launch_config)
        page = await browser.newPage()

        await page.goto('https://www.' + self.site + '.com/en/login')
        sleep = 8000
        _LOGGER.debug("Waiting for = %s millis", sleep)
        await page.waitFor(sleep)
        # await page.screenshot({'path': 'meter0.png'})

        await page.type("#form-login-email", self.email)
        await page.type("#form-login-password", self.password)
        await page.click("#form-login-remember-me")
        await page.click(".submit-button")
        # Wait for login to authenticate
        sleep = 30000
        _LOGGER.debug("Waiting for = %s millis", sleep)
        await page.waitFor(sleep)
        # await page.screenshot({'path': 'meter1.png'})

        # Enter in 2 factor auth code (see README for details)
        mfa_code = self.mfa_secret
        if self.mfa_type == self.MFA_TYPE_TOTP:
            mfa_code = pyotp.TOTP(self.mfa_secret).now()
        #_LOGGER.debug("mfa_code = %s", mfa_code)
        await page.type("#form-login-mfa-code", mfa_code)
        # await page.screenshot({'path': 'meter2.png'})
        await page.click(".js-login-new-device-form .button")
        # Wait for authentication to complete
        # await page.waitForNavigation()
        sleep = 30000
        _LOGGER.debug("Waiting for = %s millis", sleep)
        await page.waitFor(sleep)
        # await page.screenshot({'path': 'meter3.png'})

        # Access the API using your newly acquired authentication cookies!
        api_page = await browser.newPage()
        api_url = 'https://' + self.site + '.opower.com/ei/edge/apis/cws-real-time-ami-v1/cws/' + self.site + '/accounts/' + self.account_uuid + '/meters/' + self.meter_number + '/usage'
        await api_page.goto(api_url)
        # await api_page.screenshot({'path': 'meter4.png'})

        data_elem = await api_page.querySelector('pre')
        self.raw_data = await api_page.evaluate('(el) => el.textContent', data_elem)
        _LOGGER.debug(self.raw_data)

        await browser.close()
