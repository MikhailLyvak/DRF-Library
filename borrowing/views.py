from datetime import datetime

from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from book.models import Book
from borrowing.models import Borrowing


@api_view(["POST"])
def return_borrowing(request, pk=None):
    current_user = request.user
    try:
        borrowing = Borrowing.objects.get(pk=pk)
    except ObjectDoesNotExist:
        return Response(
            data="Such a borrowing doesn't exists. Check the url please",
            status=status.HTTP_400_BAD_REQUEST,
        )
    if borrowing.user_id != current_user.id:
        return Response(
            data="It's not your borrowing, you cannot return it",
            status=status.HTTP_403_FORBIDDEN,
        )
    if borrowing.actual_return_date:
        return Response(
            data="This borrowing has been already returned",
            status=status.HTTP_403_FORBIDDEN,
        )
    today = datetime.today()
    book = Book.objects.get(book__id=borrowing.book_id)
    book.inventory += 1
    borrowing.actual_return_date = today
    book.save()
    return Response(data="Borrowing returned successful", status=status.HTTP_200_OK)
