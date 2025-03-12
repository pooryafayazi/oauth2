from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
import requests
import os
from django.shortcuts import redirect
from rest_framework.views import APIView

from . import serializers
from .models import User, Profile, UserType


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = serializers.CustomTokenObtainPairSerializer


class GoogleAuthViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]

    def create(self, request):
        authorization_code = request.data.get('code')
        if not authorization_code:
            return Response({"error": "Authorization code is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            token_info = self.exchange_code_for_token(authorization_code)
            access_token = token_info.get('access_token')

            if not access_token:
                return Response({"error": "Access token is required"}, status=status.HTTP_400_BAD_REQUEST)

            user_info = self.get_user_info(access_token)
            user = self.save_user_info(user_info)

            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'email': user.email,
                'message': 'User information saved successfully.'
            }, status=status.HTTP_200_OK)

        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request):
        redirect_uri = 'http://127.0.0.1:8000/accounts/auth/google/'
        client_id = os.environ.get('SOCIAL_AUTH_GOOGLE_OAUTH2_KEY')
        scope = 'https://www.googleapis.com/auth/userinfo.email'
        auth_url = f'https://accounts.google.com/o/oauth2/v2/auth?client_id={client_id}&redirect_uri={redirect_uri}&response_type=code&scope={scope}'
        return Response({"auth_url": auth_url}, status=status.HTTP_200_OK)

    def exchange_code_for_token(self, code):
        token_url = 'https://oauth2.googleapis.com/token'
        payload = {
            'code': code,
            'client_id': os.environ.get('SOCIAL_AUTH_GOOGLE_OAUTH2_KEY'),
            'client_secret': os.environ.get('SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET'),
            'redirect_uri': 'http://127.0.0.1:8000/accounts/auth/google/',
            'grant_type': 'authorization_code',
        }
        response = requests.post(token_url, data=payload)
        response.raise_for_status()
        return response.json()

    def get_user_info(self, access_token):
        user_info_url = 'https://www.googleapis.com/oauth2/v3/userinfo'
        headers = {
            'Authorization': f'Bearer {access_token}',
        }
        response = requests.get(user_info_url, headers=headers)
        response.raise_for_status()
        return response.json()

    def save_user_info(self, user_info):
        email = user_info.get('email')
        user, created = User.objects.get_or_create(email=email, defaults={
            'is_verified': True,
            'type': UserType.costumer.value,
        })
        return user