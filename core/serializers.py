from rest_framework import serializers

from .models import Tenant, User


class TenantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tenant
        fields = [
            "id", "name", "slug", "subdomain", "contact_email",
            "contact_phone", "address", "is_active", "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id", "username", "email", "full_name", "role",
            "phone", "tenant", "is_verified", "is_active",
            "created_at",
        ]
        read_only_fields = ["id", "created_at", "tenant"]


class UserCreateSerializer(serializers.ModelSerializer):
    """Used by Super/Admin to provision users (students, teachers, ...)."""

    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = [
            "id", "username", "email", "password", "full_name",
            "role", "phone",
        ]

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user