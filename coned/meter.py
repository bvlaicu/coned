"""ConEdison Smart Energy Meter"""
import requests
import logging

_LOGGER = logging.getLogger(__name__)


class MeterError(Exception):
    pass


class Meter(object):
    """A smart energy meter of ConEdison.

    Attributes:
        meter_id: A string representing the meter's id
    """

    def __init__(self, meter_id):
        """Return a meter object whose meter id is *meter_id*"""
        self.meter_id = meter_id
        self.unit_of_measurement = 'WH'

    def last_read(self):
        """Return the last meter read in WH"""
        try:
            url = 'https://cned.opower.com/ei/edge/apis/cws-real-time-ami-v1' \
                '/cws/cned/meters/' + self.meter_id + '/usage'
            _LOGGER.debug("url = %s", url)

            response = requests.get(url, timeout=10)
            _LOGGER.debug("response = %s", response)

            jsonResponse = response.json()
            _LOGGER.debug("jsonResponse = %s", jsonResponse)

            if 'error' in jsonResponse:
                raise MeterError('Error in getting the meter data: %s',
                                 jsonResponse['error'])

            # parse the return reads and extract the most recent one
            # (i.e. last not None)
            lastRead = None
            for read in jsonResponse['reads']:
                if read['value'] is None:
                    break
                lastRead = read
            _LOGGER.debug("lastRead = %s", lastRead)

            val = lastRead['value']
            _LOGGER.debug("val = %s %s", val, self.unit_of_measurement)

            self.last_read_wh = val

            return self.last_read_wh
        except requests.exceptions.RequestException:
            raise MeterError("Error requesting meter data")
