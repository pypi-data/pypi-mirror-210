from django.urls import path
from .views import AkvoFormViewSet, CheckView, TwilioViewSet, DataViewSet


urlpatterns = [
    path("check/", CheckView.as_view({"get": "check"}), name="twilio"),
    path(
        "forms/",
        AkvoFormViewSet.as_view({"get": "list"}),
        name="twilio",
    ),
    path(
        "forms/<int:pk>/",
        AkvoFormViewSet.as_view({"get": "retrieve"}),
        name="twilio",
    ),
    path("twilio/", TwilioViewSet.as_view({"post": "create"}), name="twilio"),
    path(
        # Twilio recomend to not use extra slash
        "twilio/<int:pk>",
        TwilioViewSet.as_view({"post": "instance"}),
        name="twilio",
    ),
    path(
        "data/",
        DataViewSet.as_view({"get": "list"}),
        name="twilio",
    ),
    path(
        "data/<int:pk>/",
        DataViewSet.as_view({"get": "retrieve"}),
        name="twilio",
    ),
]
