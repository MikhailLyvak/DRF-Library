from enum import Enum

from django.db import models

from borrowing.models import Borrowing


class PaymentType(Enum):

    PAYMENT = "PAYMENT"
    FINE = "FINE"

    @classmethod
    def choices(cls):
        return tuple((i.name, i.value) for i in cls)


class PaymentStatus(Enum):

    PENDING = "PENDING"
    PAID = "PAID"

    @classmethod
    def choices(cls):
        return tuple((i.name, i.value) for i in cls)


class Payment(models.Model):

    status = models.CharField(
        max_length=63,
        choices=PaymentStatus.choices(),
        default=PaymentStatus.PENDING
    )
    type = models.CharField(
        max_length=63,
        choices=PaymentType.choices(),
        default=PaymentType.PAYMENT
    )
    borrowing_id = models.ForeignKey(Borrowing, on_delete=models.SET_NULL, null=True)
    session_url = models.URLField(max_length=255)
    session_id = models.CharField(max_length=63)
    money_to_pay = models.DecimalField(max_digits=5, decimal_places=2)


