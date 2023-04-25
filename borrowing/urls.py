from django.urls import path, include
from rest_framework import routers

from borrowing.views import BorrowingViewSet, return_borrowing


router = routers.DefaultRouter()
router.register("borrowings", BorrowingViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("borrowings/<int:pk>/return/", return_borrowing, name="return-borrowing"),
]

app_name = "borrowing"
