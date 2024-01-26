from __future__ import unicode_literals

import logging
from collections import OrderedDict

from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from django_giropay import settings as django_giropay_settings
from django_giropay.constants import SHOPPING_CART_TYPE
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
        currency='EUR', shoppingCartType=SHOPPING_CART_TYPE.ANONYMOUS_DONATION, shipping_address=None,
        merchantOrderReferenceNumber=False, kassenzeichen=False,
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

        # Ordering needs to be the same as in the API docs, otherwise the generated hash will be invalid
        data = OrderedDict()
        data['merchantId'] = self.auth['MERCHANT_ID']
        data['projectId'] = self.auth['PROJECT_ID']
        data['merchantTxId'] = merchant_tx_id
        data['amount'] = amount
        data['currency'] = currency
        data['purpose'] = purpose
        data['shoppingCartType'] = shoppingCartType
        if shipping_address:
            data['shippingAddresseFirstName'] = shipping_address.get('shippingAddresseFirstName', '')
            data['shippingAddresseLastName'] = shipping_address.get('shippingAddresseLastName', '')
            data['shippingCompany'] = shipping_address.get('shippingCompany', '')
            data['shippingAdditionalAddressInformation'] = shipping_address.get('shippingAdditionalAddressInformation',
                                                                                '')
            data['shippingStreet'] = shipping_address.get('shippingStreet', '')
            data['shippingStreetNumber'] = shipping_address.get('shippingStreetNumber', '')
            data['shippingZipCode'] = shipping_address.get('shippingZipCode', '')
            data['shippingCity'] = shipping_address.get('shippingCity', '')
            data['shippingCountry'] = shipping_address.get('shippingCountry', '')
            data['shippingEmail'] = shipping_address.get('shippingEmail', '')
        if merchantOrderReferenceNumber:
            data['merchantOrderReferenceNumber'] = merchantOrderReferenceNumber
        data['urlRedirect'] = redirect_url
        data['urlNotify'] = notify_url
        if kassenzeichen:
            data['kassenzeichen'] = kassenzeichen


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
            giropay_transaction.external_payment_url = response_dict['redirect']
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
