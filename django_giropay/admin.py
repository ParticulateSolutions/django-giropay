from django.contrib import admin

from .models import GiropayTransaction


class GiropayTransactionAdmin(admin.ModelAdmin):
    list_display = ('merchant_tx_id', 'reference', 'latest_response_code')
    list_filter = ('latest_response_code',)
    ordering = ('-created_at',)
    fields = ('merchant_tx_id', 'reference', 'latest_response_code')

admin.site.register(GiropayTransaction, GiropayTransactionAdmin)
