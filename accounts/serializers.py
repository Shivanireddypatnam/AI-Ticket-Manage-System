from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.password_validation import validate_password
from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import UserProfile

User = get_user_model()


class CustomerRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, trim_whitespace=False)

    class Meta:
        model = User
        fields = ["username", "email", "password"]

    def validate_email(self, value):
        value = value.strip().lower()
        if not value:
            raise serializers.ValidationError("Email is required.")
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError(
                "An account with this email already exists."
            )
        return value

    def validate_password(self, value):
        validate_password(value)
        return value

    @transaction.atomic
    def create(self, validated_data):
        user = User(
            username=validated_data["username"],
            email=validated_data["email"],
        )
        user.set_password(validated_data["password"])
        user.save()
        UserProfile.objects.get_or_create(
            user=user, defaults={"role": "CUSTOMER"}
        )
        return user


class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = "email"

    def validate(self, attrs):
        email = (attrs.get("email") or "").strip().lower()
        password = attrs.get("password")
        matching_users = User.objects.filter(email__iexact=email)

        if matching_users.count() != 1:
            raise AuthenticationFailed("Invalid email or password.")

        user = authenticate(
            request=self.context.get("request"),
            username=matching_users.first().get_username(),
            password=password,
        )
        if user is None or not user.is_active:
            raise AuthenticationFailed("Invalid email or password.")

        profile, _ = UserProfile.objects.get_or_create(
            user=user,
            defaults={"role": "ADMIN" if user.is_superuser else "CUSTOMER"},
        )
        refresh = self.get_token(user)
        refresh["role"] = profile.role
        refresh["email"] = user.email
        return {"refresh": str(refresh), "access": str(refresh.access_token)}
