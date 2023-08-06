import json
import logging

from perun.utils.consent_framework.consent import Consent
from perun.utils.consent_framework.consent_request import ConsentRequest
from perun.utils.consent_framework.consent_db import ConsentDB
from perun.utils.consent_framework.consent_request_db import ConsentRequestDB

logger = logging.getLogger(__name__)


class InvalidConsentRequestError(ValueError):
    pass


class ConsentManager(object):
    def __init__(self, cfg):
        self.consent_db = ConsentDB(cfg, "consent_database")
        self.ticket_db = ConsentRequestDB(cfg, "consent_database")
        self.trusted_keys = cfg["keystore"]
        self.max_months_valid = cfg["consent"]["months_valid"]

    def fetch_consented_attributes(self, consent_id: str):
        consent = self.consent_db.get_consent(consent_id)
        if consent and not consent.has_expired(self.max_months_valid):
            return consent.attributes

        logger.debug("No consented attributes for id: '%s'", consent_id)
        return

    def save_consent_request(self, jwt):
        request = jwt

        try:
            data = ConsentRequest(request)
        except ValueError:
            logger.debug("invalid consent request: %s", json.dumps(request))
            raise InvalidConsentRequestError("Invalid consent request")

        self.ticket_db.save_consent_request(request, data)
        return request

    def fetch_consent_request(self, ticket: str):
        ticket_data = self.ticket_db.get_consent_request(ticket)
        if ticket_data:
            self.ticket_db.delete_consent_request(ticket)
            logger.debug("found consent request: %s", ticket_data.data)
            return ticket_data.data
        else:
            logger.debug("failed to retrieve ticket data from ticket: %s" % ticket)
            return

    def save_consent(self, consent_id: str, consent: Consent):
        self.consent_db.save_consent(consent_id, consent)

    def delete_user_consent(self, user_id):
        self.consent_db.delete_user_consent(user_id)
