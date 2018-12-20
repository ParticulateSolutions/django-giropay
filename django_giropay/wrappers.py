from __future__ import unicode_literals

import logging

from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from django_giropay import settings as django_giropay_settings
from django_giropay.models import GiropayTransaction

import requests

from django_giropay.utils import build_giropay_full_uri

logger = logging.getLogger(__name__)


class GiropayWrapper(object):
    interface_version = 'django_giropay_v{}'.format(django_giropay_settings.DJANGO_GIROPAY_VERSION)

    api_url = django_giropay_settings.GIROPAY_API_URL
    bankstatus_url = django_giropay_settings.GIROPAY_BANKSTATUS_URL
    transaction_start_url = django_giropay_settings.GIROPAY_TRANSACTION_START_URL
    issuer_url = django_giropay_settings.GIROPAY_ISSUER_URL

    auth = None

    def __init__(self, auth=None):
        super(GiropayWrapper, self).__init__()
        if getattr(settings, 'GIROPAY', False):
            if auth:
                self.auth = auth
            else:
                self.auth = {
                    'MERCHANT_ID': django_giropay_settings.GIROPAY_MERCHANT_ID,
                    'PROJECT_ID': django_giropay_settings.GIROPAY_PROJECT_ID,
                    'PROJECT_PASSWORD': django_giropay_settings.GIROPAY_PROJECT_PASSWORD,
                }

    def start_transaction(self, merchant_tx_id, amount, purpose,
        currency='EUR', bic=False, iban=False, info_1_label=False, info_1_text=False, info_2_label=False,
        info_2_text=False, info_3_label=False, info_3_text=False, info_4_label=False, info_4_text=False,
        info_5_label=False, info_5_text=False,
        redirect_url=django_giropay_settings.GIROPAY_RETURN_URL,
        notify_url=django_giropay_settings.GIROPAY_NOTIFICATION_URL,
        success_url=django_giropay_settings.GIROPAY_SUCCESS_URL,
        error_url=django_giropay_settings.GIROPAY_ERROR_URL
    ):
        giropay_transaction = GiropayTransaction()
        giropay_transaction.merchant_id = self.auth['MERCHANT_ID']
        giropay_transaction.project_id = self.auth['PROJECT_ID']
        giropay_transaction.merchant_tx_id = merchant_tx_id
        giropay_transaction.amount = amount
        giropay_transaction.currency = currency
        giropay_transaction.purpose = purpose
        giropay_transaction.redirect_url = build_giropay_full_uri(redirect_url)
        giropay_transaction.notify_url = build_giropay_full_uri(notify_url)
        giropay_transaction.success_url = build_giropay_full_uri(success_url)
        giropay_transaction.error_url = build_giropay_full_uri(error_url)

        data = {
            'merchantId': self.auth['MERCHANT_ID'],
            'projectId': self.auth['PROJECT_ID'],
            'merchantTxId': merchant_tx_id,
            'amount': amount,
            'currency': currency,
            'purpose': purpose,
            'urlRedirect': giropay_transaction.redirect_url,
            'urlNotify': giropay_transaction.notify_url,
        }
        if bic:
            data.update({'bic': bic})
            giropay_transaction.bic = bic
        if iban:
            data.update({'iban': iban})
            giropay_transaction.iban = iban
        if info_1_label:
            data.update({'info1Label': info_1_label})
            giropay_transaction.info_1_label = info_1_label
        if info_1_text:
            data.update({'info1Text': info_1_text})
            giropay_transaction.info_1_text = info_1_text
        if info_2_label:
            data.update({'info2Label': info_2_label})
            giropay_transaction.info_2_label = info_2_label
        if info_2_text:
            data.update({'info2Text': info_2_text})
            giropay_transaction.info_2_text = info_2_text
        if info_3_label:
            data.update({'info3Label': info_3_label})
            giropay_transaction.info_3_label = info_3_label
        if info_3_text:
            data.update({'info3Text': info_3_text})
            giropay_transaction.info_3_text = info_3_text
        if info_4_label:
            data.update({'info4Label': info_4_label})
            giropay_transaction.info_4_label = info_4_label
        if info_4_text:
            data.update({'info4Text': info_4_text})
            giropay_transaction.info_4_text = info_4_text
        if info_5_label:
            data.update({'info5Label': info_5_label})
            giropay_transaction.info_5_label = info_5_label
        if info_5_text:
            data.update({'info5Text': info_5_text})
            giropay_transaction.info_5_text = info_5_text

        giropay_transaction.save()

        response = self.call_api(url=self.transaction_start_url, data=data)

        response_hash = response.headers.get('hash')
        response_dict = response.json()
        response_text = response.text

        generated_hash = self._generate_hash_from_text(response_text)

        if response_hash != generated_hash:
            logger.error(_("Response hash {} not compatible with the generated hash {}.").format(response_hash, generated_hash))

        giropay_transaction.reference = response_dict['reference']
        giropay_transaction.latest_response_code = int(response_dict['rc'])
        giropay_transaction.latest_response_msg = response_dict['msg']
        giropay_transaction.save()

        if giropay_transaction.latest_response_code != 0:
            logger.error(_("Transaction Start Response code is {} {}.").format(giropay_transaction.latest_response_code, giropay_transaction.latest_response_msg))
        else:
            giropay_transaction.reference = response_dict['reference']
            giropay_transaction.redirect_banking_url = response_dict['redirect']
            giropay_transaction.save()
        return giropay_transaction

    def call_api(self, url=None, data=None):
        if not self.auth:
            return False
        if not url.lower().startswith('http'):
            url = '{0}{1}'.format(self.api_url, url)

        generated_hash = self._generate_hash_from_dict(data)
        data.update({'hash': generated_hash})

        try:
            response = requests.post(url, data=data)
        except requests.HTTPError as e:
            logger = logging.getLogger(__name__)
            if hasattr(e, 'errno'):
                logger.error("GiroPay Error {0}({1})".format(e.errno, e.strerror))  # TODO fix error handling according to requests lib
            else:
                logger.error("GiroPay Error({0})".format(e.strerror))  # TODO fix error handling according to requests lib
        else:
            return response
        return False

    def _generate_hash_from_dict(self, data_dict):
        import hashlib
        import hmac
        data_string = "".join([str(val) for val in data_dict.values()])
        data_hash = hmac.new(self.auth['PROJECT_PASSWORD'], "{}".format(data_string).encode("utf-8"), hashlib.md5).hexdigest()
        return data_hash

    def _generate_hash_from_text(self, data_text):
        import hashlib
        import hmac
        data_hash = hmac.new(self.auth['PROJECT_PASSWORD'], data_text.encode("utf-8"), hashlib.md5).hexdigest()
        return data_hash
