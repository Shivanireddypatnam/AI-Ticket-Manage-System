from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import UserProfile
from .permissions import IsAdminRole, IsAgentRole, IsCustomerRole
from .serializers import CustomerRegistrationSerializer


class CustomerRegistrationView(CreateAPIView):
    serializer_class = CustomerRegistrationSerializer
    permission_classes = [AllowAny]


class CurrentUserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile, _ = UserProfile.objects.get_or_create(
            user=request.user,
            defaults={"role": "ADMIN" if request.user.is_superuser else "CUSTOMER"},
        )
        return Response({
            "id": request.user.pk,
            "username": request.user.username,
            "email": request.user.email,
            "role": profile.role,
        })


class AdminOnlyView(APIView):
    permission_classes = [IsAuthenticated, IsAdminRole]

    def get(self, request):
        return Response({"message": "Admin authorization successful."})


class AgentOnlyView(APIView):
    permission_classes = [IsAuthenticated, IsAgentRole]

    def get(self, request):
        return Response({"message": "Support-agent authorization successful."})


class CustomerOnlyView(APIView):
    permission_classes = [IsAuthenticated, IsCustomerRole]

    def get(self, request):
        return Response({"message": "Customer authorization successful."})
