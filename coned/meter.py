"""ConEdison or Orange and Rockland Utility Smart Energy Meter"""
import requests
import logging
import asyncio
from pyppeteer import launch
import os
import glob
import json
import pyotp


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
    DATA_SITE_CONED = 'cned'
    SITE_ORU = 'oru'
    DATA_SITE_ORU = 'oru'

    def __init__(self, email, password, mfa_type, mfa_secret, account_uuid, meter_number, account_number=None, site='coned', loop=None, browser_path=None):
        self._LOGGER = logging.getLogger(__name__)

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
        self._LOGGER.debug("mfa_type = %s", self.mfa_type)
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

        self.meter_number = meter_number.lstrip("0")
        if self.meter_number is None:
            raise MeterError("Error initializing meter data - meter_number is missing")
        # _LOGGER.debug("meter_number = %s", self.meter_number.replace(self.meter_number[:5], '*'))

        self.account_number = account_number

        self.site = site
        if site == Meter.SITE_CONED:
            self.data_site = Meter.DATA_SITE_CONED
        elif site == Meter.SITE_ORU:
            self.data_site = Meter.DATA_SITE_ORU
        self._LOGGER.debug("site = %s", self.site)
        if self.site not in [Meter.SITE_CONED, Meter.SITE_ORU]:
            raise MeterError("Error initializing meter data - unsupported site %s", self.site)

        self.loop = loop
        self._LOGGER.debug("loop = %s", self.loop)

        self.browser_path = browser_path
        self._LOGGER.debug("browser_path = %s", self.browser_path)

    async def all_reads(self):
        """Return all available meter read values and unit of measurement"""
        try:
            asyncio.set_event_loop(self.loop)
            asyncio.get_event_loop().create_task(self.browse())
            await self.browse()

            # parse the return reads and extract the most recent one
            # (i.e. last not None)
            jsonResponse = json.loads(self.raw_data)

            availableReads = []
            if 'error' in jsonResponse:
                self._LOGGER.info("got JSON error back = %s", jsonResponse['error']['details'])
                raise MeterError(jsonResponse['error']['details'])
            for read in jsonResponse['reads']:
                if read['value'] is not None:
                    availableReads.append(read)

            parsed_reads = []
            for read in availableReads:
                this_parsed_read = {}
                this_parsed_read['start_time'] = read['startTime']
                this_parsed_read['end_time'] = read['endTime']
                this_parsed_read['value'] = read['value']
                this_parsed_read['unit_of_measurement'] = jsonResponse['unit']
                parsed_reads.append(this_parsed_read)
                self._LOGGER.info("got read = %s %s %s %s", this_parsed_read['start_time'], this_parsed_read['end_time'],
                    this_parsed_read['value'], this_parsed_read['unit_of_measurement'])

            return parsed_reads
        except:
            raise MeterError("Error requesting meter data")

    async def last_read(self):
        """Return the last meter read value and unit of measurement"""
        all_available_reads = await self.all_reads()
        last_read = all_available_reads[-1]
        return last_read['start_time'], last_read['end_time'], last_read['value'], last_read['unit_of_measurement']

    async def browse(self):
        screenshotFiles = glob.glob('meter*.png')
        for filePath in screenshotFiles:
            try:
                os.remove(filePath)
            except:
                self._LOGGER.debug("Error while deleting file : ", filePath)


        browser_launch_config = {
            "defaultViewport": {"width": 1920, "height": 1080},
            "dumpio": True,
            "args": ["--no-sandbox", "--disable-gpu", "--disable-software-rasterizer"]}
        if self.browser_path is not None:
            browser_launch_config['executablePath'] = self.browser_path
        self._LOGGER.debug("browser_launch_config = %s", browser_launch_config)

        browser = await launch(browser_launch_config)
        page = await browser.newPage()

        # page.on('request', lambda req: asyncio.ensure_future(request_interception(req)))
        # page.on('response', lambda res: asyncio.ensure_future(resp(res)))

        await page.goto('https://www.' + self.site + '.com/en/login', {'waitUntil': 'domcontentloaded', 'timeout': 10000})
        # sleep = 8000
        # self._LOGGER.debug("Waiting for = %s millis", sleep)
        # await page.waitFor(sleep)
        element = await page.querySelector('#form-login-email')
        await page.screenshot({'path': 'meter1-1.png'})
        self._LOGGER.debug('meter1-1')

        await page.type("#form-login-email", self.email)
        await page.type("#form-login-password", self.password)
        # await page.click("#form-login-remember-me")
        await page.screenshot({'path': 'meter1-2.png'})
        await page.click(".submit-button")
        # # Wait for login to authenticate
        # sleep = 30000
        # self._LOGGER.debug("Waiting for = %s millis", sleep)
        # await page.waitFor(sleep)
        await fetch_element(page, '.js-login-new-device-form-selector:not(.hidden)')
        # if mfa_form is None:
        #     logging.error('Never got MFA prompt. Aborting!')
        #     return
        await fetch_element(page, '#form-login-mfa-code')
        await page.screenshot({'path': 'meter2-1.png'})
        self._LOGGER.debug('meter2-1')

        # Enter in 2 factor auth code (see README for details)
        mfa_code = self.mfa_secret
        if self.mfa_type == self.MFA_TYPE_TOTP:
            mfa_code = pyotp.TOTP(self.mfa_secret).now()
        #self._LOGGER.debug("mfa_code = %s", mfa_code)
        await page.type("#form-login-mfa-code", mfa_code)
        await page.screenshot({'path': 'meter2-2.png'})
        await page.click(".js-login-new-device-form .button")
        # Wait for authentication to complete
        # await page.waitForNavigation()
        sleep = 5000
        self._LOGGER.debug("Waiting for = %s millis", sleep)
        await page.waitFor(sleep)
        # await fetch_element(page, '#mainContent > div > div.dashboard-header-wrapper.coned-tabs--visible.js-module > div.dashboard-header.dashboard-header--oru.content-gutter > div.coned-tabs.js-coned-tabs-dropdown.js-coned-tabs.coned-tabs--oru > div:nth-child(2) > button > span')
        await page.screenshot({'path': 'meter3-1.png'})
        self._LOGGER.debug('meter3-1')

        page.on('response', lambda res: asyncio.ensure_future(resp(res, self)))

        if self.account_number:
            account_page_url = 'https://www.' + self.site + '.com/en/accounts-billing/dashboard?account=' + self.account_number
            self._LOGGER.debug(account_page_url)
            await page.goto(account_page_url)
            await page.screenshot({'path': 'meter3-0.png'})
            self._LOGGER.debug('meter3-0')
            sleep = 30000
            self._LOGGER.debug("Waiting for = %s millis", sleep)
            await page.waitFor(sleep)
        else:
            usage_page_url = 'https://www.' + self.site + '.com/en/accounts-billing/dashboard?tab1=billingandusage-1&tab3=sectionRealTimeData-3'
            self._LOGGER.debug(usage_page_url)
            await page.goto(usage_page_url, {'waitUntil': 'domcontentloaded', 'timeout': 10000})
            # await page.waitForNavigation()
            await page.screenshot({'path': 'meter3-1.png'})
            self._LOGGER.debug('meter3-1')
            sleep = 30000
            self._LOGGER.debug("Waiting for = %s millis", sleep)
            await page.waitFor(sleep)

        # # Access the API using your newly acquired authentication cookies!
        # # api_page = await browser.newPage()
        # api_url = 'https://' + self.data_site + '.opower.com/ei/edge/apis/cws-real-time-ami-v1/cws/' + self.data_site + '/accounts/' + self.account_uuid + '/meters/' + self.meter_number + '/usage'
        # await page.goto(api_url)
        # await page.screenshot({'path': 'meter4-1.png'})
        self._LOGGER.debug('meter4-1')

        self._LOGGER.debug(f"raw_data = {raw_data}")

        self.raw_data = raw_data

        # data_elem = await page.querySelector('pre')
        # self.raw_data = await page.evaluate('(el) => el.textContent', data_elem)
        #self._LOGGER.info(self.raw_data)

        await browser.close()


async def resp(res, meter):
    res.__setattr__('_allowInterception', True)
    if 'cws-real-time-ami-v1' in res.url and 'usage' in res.url:
        print(f"  res.url: {res.url}")
        print(f"  res.status: {res.status}")
        global raw_data
        raw_data = await res.text()
        meter._LOGGER.debug(f"  res.text: {raw_data}")
    pass


async def fetch_element(page, selector, max_tries=10):
    tries = 0
    el = None
    while el == None and tries < max_tries:
        el = await page.querySelector(selector)
        await page.waitFor(1000)

    return el
