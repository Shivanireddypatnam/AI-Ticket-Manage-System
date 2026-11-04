from django.urls import path

from .views import (
    AdminOnlyView,
    AgentOnlyView,
    CustomerOnlyView,
    CurrentUserView,
    CustomerRegistrationView,
)

urlpatterns = [
    path("register/", CustomerRegistrationView.as_view(), name="customer-register"),
    path("me/", CurrentUserView.as_view(), name="current-user"),
    path("admin-only/", AdminOnlyView.as_view(), name="admin-only"),
    path("agent-only/", AgentOnlyView.as_view(), name="agent-only"),
    path("customer-only/", CustomerOnlyView.as_view(), name="customer-only"),
]
