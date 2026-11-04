from django.shortcuts import render

# Create your views here.

from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny

from .serializers import CustomerRegistrationSerializer


class CustomerRegistrationView(CreateAPIView):

    serializer_class = CustomerRegistrationSerializer
    permission_classes = [AllowAny]