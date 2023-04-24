from django.db import models
from django.utils.translation import gettext_lazy as _


class Book(models.Model):

    class Cover(models.TextChoices):
        SOFT = "S", _("Soft")
        HARD = "H", _("Hard")

    title = models.CharField(max_length=63)
    author = models.CharField(max_length=255)
    cover = models.CharField(
        max_length=1,
        choices=Cover.choices,
        default=Cover.HARD

    )
    inventory = models.PositiveIntegerField()
    daily_fee = models.DecimalField(max_digits=5, decimal_places=2)
