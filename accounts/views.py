from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.core import signing
from google.auth.exceptions import GoogleAuthError

from .google_oauth import STATE_SALT

from .models import UserProfile
from .permissions import IsAdminRole, IsAgentRole, IsCustomerRole
from .serializers import CustomerRegistrationSerializer

from django.shortcuts import redirect


from .google_oauth import (
    create_oauth_state,
    build_google_authorization_url,
)
import secrets
import requests

from django.conf import settings
from django.contrib.auth import get_user_model
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from rest_framework_simplejwt.tokens import RefreshToken



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

class GoogleLoginView(APIView):

    permission_classes = [AllowAny]

    def get(self, request):

        state, nonce = create_oauth_state()

        request.session["google_oauth_state"] = state
        request.session["google_oauth_nonce"] = nonce

        google_url = build_google_authorization_url(
            state,
            nonce
        )

        return redirect(google_url)


class GoogleCallbackView(APIView):

    permission_classes = [AllowAny]

    def get(self, request):

        # 1. Get authorization code and state from Google
        code = request.query_params.get("code")
        state = request.query_params.get("state")

        if request.query_params.get("error"):
            return Response(
                {"error": "Google authentication was cancelled."},
                status=400
            )

        if not code or not state:
            return Response(
                {"error": "Authorization code or state is missing."},
                status=400
            )

        # 2. Verify OAuth state
        saved_state = request.session.get("google_oauth_state")
        saved_nonce = request.session.get("google_oauth_nonce")

        if not saved_state or not saved_nonce:
            return Response(
                {"error": "OAuth session expired. Please try again."},
                status=400
            )

        if not secrets.compare_digest(state, saved_state):
            return Response(
                {"error": "Invalid OAuth state."},
                status=400
            )

        try:
            state_data = signing.loads(
                state,
                salt=STATE_SALT,
                max_age=600
            )
        except signing.BadSignature:
            return Response(
                {"error": "Invalid or expired OAuth state."},
                status=400
            )

        if not secrets.compare_digest(
            state_data.get("nonce", ""),
            saved_nonce
        ):
            return Response(
                {"error": "Invalid OAuth nonce."},
                status=400
            )

        # 3. Exchange authorization code for Google tokens
        try:
            token_response = requests.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "code": code,
                    "client_id": settings.GOOGLE_CLIENT_ID,
                    "client_secret": settings.GOOGLE_CLIENT_SECRET,
                    "redirect_uri": settings.GOOGLE_REDIRECT_URI,
                    "grant_type": "authorization_code",
                },
                timeout=15
            )

            token_response.raise_for_status()
            google_tokens = token_response.json()

            # 4. Verify Google's ID token
            google_id_token = google_tokens.get("id_token")

            if not google_id_token:
                return Response(
                    {"error": "Google ID token is missing."},
                    status=400
                )

            google_user = id_token.verify_oauth2_token(
                google_id_token,
                google_requests.Request(),
                settings.GOOGLE_CLIENT_ID
            )

            if not secrets.compare_digest(
                google_user.get("nonce", ""),
                saved_nonce
            ):
                return Response(
                    {"error": "Google token nonce verification failed."},
                    status=400
                )

            email = google_user.get("email")

            if not email or not google_user.get("email_verified"):
                return Response(
                    {"error": "A verified Google email is required."},
                    status=400
                )

        except (requests.RequestException, GoogleAuthError, ValueError) as error:
          print("GOOGLE OAUTH DEBUG ERROR:", repr(error))

          return Response(
            {"error": "Google authentication failed."},
            status=400
      )

        # 5. Find or create Django user
        User = get_user_model()

        user = User.objects.filter(email__iexact=email).first()

        if user is None:

            base_username = email.split("@")[0]
            username = base_username
            counter = 1

            while User.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1

            user = User.objects.create_user(
                username=username,
                email=email
            )

        # 6. Get existing profile without changing its role
        profile, _ = UserProfile.objects.get_or_create(
            user=user,
            defaults={"role": "CUSTOMER"}
        )

        # 7. Generate our existing JWT tokens
        refresh = RefreshToken.for_user(user)

        # 8. Clear OAuth session data
        request.session.pop("google_oauth_state", None)
        request.session.pop("google_oauth_nonce", None)

        return Response({
            "message": "Google login successful.",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": profile.role,
            },
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        })
