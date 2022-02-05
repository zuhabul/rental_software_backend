from django.urls import path
from product import views

app_name = "product"
urlpatterns = [
    path("", views.ListCreateProductAPIView.as_view(), name="product_create_list"),
    path(
        "<int:pk>/",
        views.RetrieveUpdateDestroyProductAPIView.as_view(),
        name="product_retrive_delete_update",
    ),
]
