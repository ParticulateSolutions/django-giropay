from django.conf import settings

from django_giropay.__init__ import __version__

DJANGO_GIROPAY_VERSION = __version__

GIROPAY_MERCHANT_ID = getattr(settings, 'GIROPAY_MERCHANT_ID', "1234567")
GIROPAY_PROJECT_ID = getattr(settings, 'GIROPAY_PROJECT_ID', "1234")
GIROPAY_PROJECT_PASSWORD = getattr(settings, 'GIROPAY_PROJECT_PASSWORD', b'secure')

GIROPAY_VALID_TRANSACTION_STATUSES = getattr(settings, 'GIROPAY_VALID_TRANSACTION_STATUSES', [4000])

GIROPAY_API_URL = getattr(settings, 'GIROPAY_API_URL', 'https://payment.girosolution.de')

GIROPAY_BANKSTATUS_URL = getattr(settings, 'GIROPAY_BANKSTATUS_URL', '/girocheckout/api/v2/giropay/bankstatus')
GIROPAY_TRANSACTION_START_URL = getattr(settings, 'GIROPAY_TRANSACTION_START_URL', '/girocheckout/api/v2/transaction/start')
GIROPAY_ISSUER_URL = getattr(settings, 'GIROPAY_ISSUER_URL', '/girocheckout/api/v2/giropay/issuer')

# checkout urls
GIROPAY_RETURN_URL = getattr(settings, 'GIROPAY_RETURN_URL', '/giropay/return/')
GIROPAY_SUCCESS_URL = getattr(settings, 'GIROPAY_SUCCESS_URL', '/')
GIROPAY_ERROR_URL = getattr(settings, 'GIROPAY_ERROR_URL', '/')
GIROPAY_CANCELLATION_URL = getattr(settings, 'GIROPAY_CANCELLATION_URL', '/')
GIROPAY_NOTIFICATION_URL = getattr(settings, 'GIROPAY_NOTIFICATION_URL', '/giropay/notify/')

if getattr(settings, 'GIROPAY', False):
    GIROPAY_ROOT_URL = settings.GIROPAY_ROOT_URL
