"""Script used to define the paystack Transaction class."""

from ktechpayapi.base import KtechPayBase


class Transaction(KtechPayBase):
    """docstring for Transaction."""

    @classmethod
    def initialize(cls, **kwargs):
        """
        Initialize transaction.

        Args:
            amount: amount
            email: email address

        Returns:
            Json data from ktechpay API.
        """

        return cls().requests.post("payments/", data=kwargs)

    @classmethod
    def list(cls):
        """
        List transactions.

        Args:
            No argument required.

        Returns:
            Json data from ktechpay API.
        """
        return cls().requests.get("payments/")

    @classmethod
    def verify(cls, reference):
        """
        Verify transactions.

        Args:
            reference: a unique value needed for transaction.

        Returns:
            Json data from ktechpay API.
        """
        return cls().requests.get(f"payments/{reference}")
