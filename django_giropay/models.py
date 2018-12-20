from __future__ import unicode_literals

import logging

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _



@python_2_unicode_compatible
class GiropayTransaction(models.Model):
    created_at = models.DateTimeField(_("created_at"), auto_now_add=True)

    reference = models.TextField(_("reference"), null=True)
    backend_tx_id = models.TextField(_("backend tx id"), null=True)
    merchant_tx_id = models.CharField(_("merchant tx id"), max_length=255, unique=True)

    merchant_id = models.IntegerField(_("amount in Cents"))
    project_id = models.IntegerField(_("amount in Cents"))

    amount = models.PositiveIntegerField(_("amount in Cents"))
    currency = models.CharField(_("Currency Code (3 Chars)"), max_length=3, default='EUR')
    purpose = models.CharField(_("purpose"), max_length=27)

    iban = models.CharField(_("iban"), max_length=34, null=True, blank=True)
    bic = models.CharField(_("bic"), max_length=11, null=True, blank=True)

    redirect_url = models.TextField(_("redirect url"))
    notify_url = models.TextField(_("notify url"))

    external_payment_url = models.TextField(_("redirect url to users online banking"), null=True, blank=True)

    success_url = models.TextField(_("success url"))
    error_url = models.TextField(_("error url"))

    info_1_label = models.CharField(_("info 1 label"), max_length=30, null=True, blank=True)
    info_1_text = models.CharField(_("info 1 text"), max_length=80, null=True, blank=True)

    info_2_label = models.CharField(_("info 2 label"), max_length=30, null=True, blank=True)
    info_2_text = models.CharField(_("info 2 text"), max_length=80, null=True, blank=True)

    info_3_label = models.CharField(_("info 3 label"), max_length=30, null=True, blank=True)
    info_3_text = models.CharField(_("info 3 text"), max_length=80, null=True, blank=True)

    info_4_label = models.CharField(_("info 4 label"), max_length=30, null=True, blank=True)
    info_4_text = models.CharField(_("info 4 text"), max_length=80, null=True, blank=True)

    info_5_label = models.CharField(_("info 5 label"), max_length=30, null=True, blank=True)
    info_5_text = models.CharField(_("info 5 text"), max_length=80, null=True, blank=True)

    result_payment = models.IntegerField(_("return code from giropay transaction"), null=True)
    result_avs = models.IntegerField(_("return code of giropay age verification"), null=True, blank=True)  # giropay-ID
    obv_name = models.TextField(_("obv name"), null=True, blank=True)  # giropay-ID

    latest_response_code = models.IntegerField(_("rc field from giropay response"), null=True)  # returned by giropay when calling their API
    latest_response_msg = models.TextField(_("msg field from giropay response"), blank=True, null=True)  # empty when no error

    objects = models.Manager()

    def __str__(self):
        return self.merchant_tx_id

    class Meta:
        verbose_name = _("Giropay Transaction")
        verbose_name_plural = _("Giropay Transaction")
