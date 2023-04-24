from django.db import models
from django.utils.translation import gettext_lazy as _

from borrowing.models import Borrowing


class Payment(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", _("Pending")
        PAID = "PAID", _("Paid")

    class Type(models.TextChoices):
        PAYMENT = "PAYMENT", _("Payment")
        FINE = "FINE", _("Fine")

    status = models.CharField(
        max_length=7,
        choices=Status.choices,
        default=Status.PENDING
    )
    type =  models.CharField(
        max_length=7,
        choices=Type.choices,
        default=Type.PAYMENT
    )
    borrowing_id = models.ForeignKey(Borrowing, on_delete=models.SET_NULL)
    session_url = models.URLField(max_length=255)
    session_id = models.CharField(max_length=63)
    money_to_pay = models.DecimalField(max_digits=5, decimal_places=2)


