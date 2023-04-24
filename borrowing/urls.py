from django.urls import path

from borrowing.views import return_borrowing

urlpatterns = [
    path("<int:pk>/return/", return_borrowing, name="return-borrowing"),
]
