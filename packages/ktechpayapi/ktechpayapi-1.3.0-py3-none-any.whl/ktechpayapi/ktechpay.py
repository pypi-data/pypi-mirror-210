"""Entry point defined here."""
from ktechpayapi.transaction import Transaction
from ktechpayapi.base import KtechPayBase


class Kteckpay(KtechPayBase):
    """Base class defined for KtechPay Instance Method."""

    def __init__(self, ktech_secret_key=None):
        KtechPayBase.__init__(self, ktech_secret_key=ktech_secret_key)

        self.transaction = Transaction
