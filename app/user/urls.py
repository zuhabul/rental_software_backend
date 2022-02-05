from django.urls import path, include

from user import views

app_name = "user"

urlpatterns = [
    path('oauth/', include('oauth2_provider.urls', namespace='oauth2_provider')),
    path(
        "oauth/create/",
        views.UserCreateView.as_view(),
        name="User Create",
    ),
    path(
        "oauth/login/",
        views.UserLoginView.as_view(),
        name="User Login",
    ),
    path(
        "oauth/logout/",
        views.UserLogoutView.as_view(),
        name="User Logout",
    ),
    path('',
         views.UserAPIView.as_view(), name='session_create_list'),
    path(
        "<int:pk>/",
        views.RetrieveUpdateDestroyUserAPIView.as_view(),
        name="session_retrive_delete_update",
    ),
    path(
        "me/update/",
        views.CoreUserUpdateView.as_view(),
        name="user_update",
    ),
]
