from django.urls import path

from .views import BatchManager

urlpatterns = [
    path("", BatchManager.as_view(), name="Batch Manager"),
]
