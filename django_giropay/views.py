import logging

from django.http import HttpResponse
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View, RedirectView

from django_giropay.constants import RESULT_PAYMENT_STATUS
from django_giropay.models import GiropayTransaction

from django_giropay.wrappers import GiropayWrapper
from django_giropay import settings as django_giropay_settings

logger = logging.getLogger(__name__)


def validate_giropay_get_params(giropay_wrapper, get_params):
    desired_variables = ['gcReference', 'gcMerchantTxId', 'gcBackendTxId', 'gcAmount', 'gcCurrency', 'gcResultPayment', 'gcHash']

    # check for expected parameters
    if not all([var in get_params for var in desired_variables]):
        logger.error(
            _("Not all desired variables where part of the GiroPay Notification. Payload: {}").format(str(get_params))
        )
        return False

    # calculate hash and compare
    notification = {key: value for key, value in get_params.items() if key.startswith('gc')}
    notification_hash = notification.pop('gcHash')
    generated_hash = giropay_wrapper._generate_hash_from_dict(notification)

    if generated_hash != notification_hash:
        return False

    return True


class NotifyGiropayView(View):

    def get(self, request, *args, **kwargs):
        giropay_wrapper = GiropayWrapper()
        get_params = request.GET

        if not validate_giropay_get_params(giropay_wrapper, get_params):
            return HttpResponse(status=400)

        try:
            giropay_transaction = GiropayTransaction.objects.get(reference=get_params['gcReference'])
        except GiropayTransaction.DoesNotExist:
            return HttpResponse(status=400)

        giropay_transaction.result_payment = int(get_params['gcResultPayment'])
        giropay_transaction.backend_tx_id = get_params['gcBackendTxId']
        giropay_transaction.save()

        return self.handle_updated_transaction(giropay_transaction=giropay_transaction)

    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        return super(NotifyGiropayView, self).dispatch(request, *args, **kwargs)

    def handle_updated_transaction(self, giropay_transaction, expected_statuses=django_giropay_settings.GIROPAY_VALID_TRANSACTION_STATUSES):
        """
            Override to use the giropay_transaction in the way you want.
        """
        if giropay_transaction.result_payment not in expected_statuses:
            logger.error(
                _("GiroPay Result faulty: {}").format(RESULT_PAYMENT_STATUS[giropay_transaction.result_payment] if giropay_transaction.result_payment in RESULT_PAYMENT_STATUS else giropay_transaction.result_payment)
            )
            return HttpResponse(status=400)
        return HttpResponse(status=200)


class GiropayReturnView(RedirectView):
    giropay_wrapper = GiropayWrapper()

    def get_error_url(self):
        return django_giropay_settings.GIROPAY_ERROR_URL

    def get_cancel_url(self, giropay_transaction):
        return giropay_transaction.error_url

    def get_success_url(self, giropay_transaction):
        return giropay_transaction.success_url

    def get_redirect_url(self, *args, **kwargs):
        get_params = self.request.GET

        if not validate_giropay_get_params(self.giropay_wrapper, get_params):
            return self.get_error_url()

        try:
            giropay_transaction = GiropayTransaction.objects.get(reference=get_params['gcReference'])
        except GiropayTransaction.DoesNotExist:
            return self.get_error_url()

        giropay_transaction.result_payment = int(get_params['gcResultPayment'])
        giropay_transaction.backend_tx_id = get_params['gcBackendTxId']
        giropay_transaction.save()

        if giropay_transaction.result_payment not in django_giropay_settings.GIROPAY_VALID_TRANSACTION_STATUSES:
            return self.get_cancel_url(giropay_transaction)
        return self.get_success_url(giropay_transaction)
