from django.urls import path, re_path

from .views import BatchManager, ConsultationManager

urlpatterns = [
    path(
        "",
        BatchManager.as_view(),
        name="Batch Manager",
    ),
    re_path(
        r"^/consultation/?(?P<consultation_id>.{0,40})",
        ConsultationManager.as_view(),
        name="Consultation Manager",
    ),
]
