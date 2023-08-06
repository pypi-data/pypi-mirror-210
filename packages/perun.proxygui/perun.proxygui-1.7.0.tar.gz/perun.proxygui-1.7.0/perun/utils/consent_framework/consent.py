import logging
from datetime import datetime

from dateutil import relativedelta

LOGGER = logging.getLogger(__name__)


class Consent(object):
    def __init__(self, attributes, user_id, requester, months_valid, timestamp=None):
        """
        :param attributes: all attribute the user has given consent for. None implies
               that consent has been given for all attributes
        :param months_valid: policy for how long the consent is valid in months
        :param timestamp: datetime for when the consent was created
        """
        if not timestamp:
            timestamp = datetime.utcnow()
        self.timestamp = timestamp
        self.user_id = user_id
        self.requester = requester
        self.attributes = attributes
        self.months_valid = months_valid

    def has_expired(self, max_months_valid: int):
        """
        :param max_months_valid: maximum number of months any consent should be valid
        :return: True if this consent has expired, else False
        """
        delta = relativedelta.relativedelta(datetime.utcnow(), self.timestamp)
        months_since_consent = delta.years * 12 + delta.months
        return months_since_consent > min(self.months_valid, max_months_valid)
