from rest_framework.permissions import IsAuthenticated
from product.serializers import ProductSerializer
from core.models import ProductModel
from rest_framework.generics import RetrieveUpdateDestroyAPIView, ListCreateAPIView


def get_or_none(classmodel, **kwargs):
    try:
        return classmodel.objects.get(**kwargs)
    except classmodel.DoesNotExist:
        return None


class ListCreateProductAPIView(ListCreateAPIView):
    serializer_class = ProductSerializer
    queryset = ProductModel.objects.all()
    # permission_classes = [
    #     IsAuthenticated,
    # ]


class RetrieveUpdateDestroyProductAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = ProductSerializer
    queryset = ProductModel.objects.all()
    # permission_classes = [
    #     IsAuthenticated,
    # ]


