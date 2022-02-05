from django.contrib.auth import get_user_model, authenticate
from rest_framework import serializers
from django.utils.translation import gettext_lazy as _


class BasicUserSerializer(serializers.ModelSerializer):
    """Serializers for the user objects"""

    class Meta:
        model = get_user_model()
        fields = ("email", "password")
        extra_kwargs = {
            "password": {
                "min_length": 5,
                "write_only": True,
            }
        }

    def create(self, validated_data):
        """Create a new user with encrypted password and return it and overwrite default one"""
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        """Update a user, setting the password correctly and return it"""

        password = validated_data.pop("password", None)
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()
        return user


class UserSerializer(serializers.ModelSerializer):
    """Serializers for the user objects"""

    class Meta:
        model = get_user_model()
        fields = (
            "id",
            "email",
            "is_superuser",
            "is_active",
            "is_staff",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
            "last_login",
        )


class UserUpdateDataSerializer(serializers.ModelSerializer):
    """Serializers for the user objects"""

    class Meta:
        model = get_user_model()
        fields = "__all__"


class LoginSerializer(serializers.Serializer):
    """Serializer for the user authentication object"""

    email = serializers.EmailField()
    password = serializers.CharField(
        style={"input_type": "password"}, trim_whitespace=False
    )

    def validate(self, attrs):
        """Validate and authenticate the user"""
        email = attrs.get("email")
        password = attrs.get("password")

        user = authenticate(
            request=self.context.get("request"),
            username=email,
            password=password,
        )
        if not user:
            msg = "Unable to authenticate with provided information"
            raise serializers.ValidationError(msg, code="authenticate")

        attrs["user"] = user
        return attrs


class LogoutSerializer(serializers.Serializer):
    """Serializer which accepts an OAuth2 access token and logs out user"""

    token = serializers.CharField(max_length=4096, required=True, trim_whitespace=True)


class ResetPasswordSerializer(serializers.Serializer):
    """Serializer for password reset"""

    old_password = serializers.CharField(max_length=128, required=True)
    new_password = serializers.CharField(max_length=128, required=True)
