from django.urls import path, include
from .views import ProtectedTestView

urlpatterns = [
    path('accounts/', include('accounts.urls')),
    path('protected/', ProtectedTestView.as_view(), name='protected-api'),
]