from enum import Enum

from django.db import models


class BookCover(Enum):

    SOFT = "SOFT"
    HARD = "HARD"

    @classmethod
    def choices(cls):
        print(tuple((i.name, i.value) for i in cls))
        return tuple((i.name, i.value) for i in cls)


class Book(models.Model):
    title = models.CharField(max_length=63)
    author = models.CharField(max_length=255)
    cover = models.CharField(
        max_length=63,
        choices=BookCover.choices(),
        default=BookCover.HARD

    )
    inventory = models.PositiveIntegerField()
    daily_fee = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self) -> str:
        return self.title
