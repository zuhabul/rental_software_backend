# from user.serializers import BasicUserSerializer
from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from core.models import ProductModel
from django_currentuser.middleware import get_current_user


class ProductSerializer(serializers.ModelSerializer):
    """Serializer for Creating School"""

    class Meta:
        model = ProductModel
        depth = 0
        fields = "__all__"
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
        ]

        def perform_create(self, serializer):
            serializer.save(created_by=get_current_user)
