# django-giropay [![Build Status](https://travis-ci.org/ParticulateSolutions/django-giropay.svg?branch=master)](https://travis-ci.org/ParticulateSolutions/django-giropay)

`django-giropay` is a lightweight [django](http://djangoproject.com) plugin which provides the integration of the payment service [giropay](https://www.giropay.de/).

## How to install django-giropay?

There are just two steps needed to install django-giropay:

1. Install django-giropay to your virtual env:

	```bash
	pip install django-giropay
	```

2. Configure your django installation with the following lines:

	```python
    # django-giropay
    INSTALLED_APPS += ('django_giropay', )

    GIROPAY = True
    GIROPAY_ROOT_URL = 'http://example.com'

    # Those are dummy test data - change to your data
    GIROPAY_MERCHANT_ID = "from-payment-provider"
    GIROPAY_PROJECT_ID = "from-payment-provider"
    GIROPAY_PROJECT_PASSWORD = b"from-payment-provider"
	```

    There is a list of other settings you could set down below.

3. Include the notification View in your URLs:

	```python
    # urls.py
    from django.conf.urls import include, url

    urlpatterns = [
        url('^giropay/', include('django_giropay.urls')),
    ]
	```

## What do you need for django-giropay?

1. An merchant account for Giropay
2. Django >= 1.11

## Usage

### Minimal Checkout init example:

```python
from django_giropay.wrappers import GiropayWrapper
giropay_wrapper = GiropayWrapper()

giropay_transaction = giropay_wrapper.start_transaction(
    merchant_tx_id='first-test',
    amount=1000,  # 10 Euro 
    purpose='first test'
)
```

## Customize

You may want to customize django-giropay to fit your needs.

### Settings

The first and most straight forward way to customize it, is to adjust the settings.

… to be done …

### Method overrides

There are a few methods in the NotificationView you may want to override to match your system.

```python
class MyNotifyGiropayView(NotifyGiropayView):

    # For all checkouts you want to customize the status callback method
    def handle_updated_transaction(self, giropay_transaction, expected_statuses=django_giropay_settings.GIROPAY_VALID_TRANSACTION_STATUSES):
        # Be sure to check whether the giropay status is in a valid status
        if giropay_transaction.result_payment not in expected_statuses:
            logger.error(
                _("GiroPay Result faulty: {}").format(RESULT_PAYMENT_STATUS[giropay_transaction.result_payment] if giropay_transaction.result_payment in RESULT_PAYMENT_STATUS else giropay_transaction.result_payment)
            )
            # do whateveer you want here
            return HttpResponse(status=400)
        # or do whateveer you want
        return HttpResponse(status=200)
```

### Sandbox/Production Switch

There is no sandbox/production switch at Giropay.

## Copyright and license

Copyright 2018 Particulate Solutions GmbH, under [MIT license](https://github.com/ParticulateSolutions/django-giropay/blob/master/LICENSE).
