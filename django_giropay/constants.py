from django.utils.translation import gettext as _


RESULT_PAYMENT_STATUS = {
    4000: _("4000 Transaction successful"),
    4001: _("4001 Bank offline"),
    4002: _("4002 Online banking account invalid"),
    4500: _("4500 Unknown payment result"),
    4051: _("4051 Invalid bank account"),
    4101: _("4101 Issuing country invalid or unknown"),
    4102: _("4102 3D-Secure or MasterCard SecureCode authorization failed"),
    4103: _("4103 Validation date of card exceeded"),
    4104: _("4104 Invalid or unknown card type"),
    4105: _("4105 Limited-use card"),
    4106: _("4106 Invalid pseudo-cardnumber"),
    4107: _("4107 Card stolen, suspicious or marked to move in"),
    4108: _("4108 Telephone approval"),
    4151: _("4151 Invalid PayPal token"),
    4152: _("4152 Post-processing necessary at PayPal"),
    4153: _("4153 Change PayPal payment method"),
    4154: _("4154 PayPal-payment is not completed"),
    4501: _("4501 Timeout / no user input"),
    4502: _("4502 User aborted"),
    4503: _("4503 Duplicate transaction"),
    4504: _("4504 Uspicion of manipulation or payment method temporarily blocked"),
    4505: _("4505 Payment method blocked or rejected"),
    4506: _("4506 Invalid Blue Code barcode"),
    4900: _("4900 Transaction rejected"),
}

AGE_VERIFICATION_STATUS = {
    4020: _("4020 Age verification successful"),
    4021: _("4021 Age verification not possible"),
    4022: _("4022 Age verification unsuccessful"),
}

class SHOPPING_CART_TYPE:
    PHYSICAL = 'PHYSICAL'
    DIGITAL = 'DIGITAL'
    MIXED = 'MIXED'
    ANONYMOUS_DONATION = 'ANONYMOUS_DONATION'
    AUTHORITIES_PAYMENT = 'AUTHORITIES_PAYMENT'
