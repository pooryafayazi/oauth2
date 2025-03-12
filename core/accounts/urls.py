from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

from . import views


app_name = 'accounts'


urlpatterns = [
            # login jwt
    path("jwt/create/", views.CustomTokenObtainPairView.as_view(), name="jwt-create"),
    path("jwt/refresh/", TokenRefreshView.as_view(), name="jwt-refresh"),
    path("jwt/verify/", TokenVerifyView.as_view(), name="jwt-verify"),

    path('accounts/auth/google/', views.GoogleAuthViewSet.as_view({'post': 'create', 'get': 'list',}), name='google-auth'),
]