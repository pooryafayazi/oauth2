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


"""
def exchange_code_for_token(authorization_code):
    token_url = 'https://oauth2.googleapis.com/token'
    payload = {
        'code': authorization_code,
        'client_id': os.environ.get('SOCIAL_AUTH_GOOGLE_OAUTH2_KEY'),
        'client_secret': os.environ.get('SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET'),
        'redirect_uri': 'http://127.0.0.1:8000/swagger/',
        'grant_type': 'authorization_code'
    }

    response = requests.post(token_url, data=payload)
    return response.json()
"""


def exchange_code_for_token(authorization_code):
    token_url = 'https://oauth2.googleapis.com/token'
    payload = {
        'code': authorization_code,
        'client_id': os.environ.get('SOCIAL_AUTH_GOOGLE_OAUTH2_KEY'),
        'client_secret': os.environ.get('SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET'),
        'redirect_uri': 'http://127.0.0.1:8000/swagger/',
        'grant_type': 'authorization_code'
    }

    response = requests.post(token_url, data=payload)
    if response.status_code != 200:
        raise ValueError(f"Failed to exchange code for token: {response.json()}")
    return response.json() 

def save_user_info(user_info):
    email = user_info.get('email')
    if not email:
        raise ValueError("Email is required")

    user, created = User.objects.get_or_create(email=email, defaults={
        'is_verified': True,
        'type': UserType.costumer.value,
    })
    return user

def get_user_info(access_token):
    user_info_url = 'https://www.googleapis.com/oauth2/v1/userinfo?alt=json'
    response = requests.get(user_info_url, headers={'Authorization': f'Bearer {access_token}'})
    
    if response.status_code != 200:
        raise ValueError(f"Failed to fetch user info: {response.json()}")

    return response.json()



class GoogleAuthView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        redirect_uri = 'http://127.0.0.1:8000/accounts/auth/google/'
        client_id = os.environ.get('SOCIAL_AUTH_GOOGLE_OAUTH2_KEY')
        scope = 'https://www.googleapis.com/auth/userinfo.email'
        auth_url = f'https://accounts.google.com/o/oauth2/v2/auth?client_id={client_id}&redirect_uri={redirect_uri}&response_type=code&scope={scope}'
        return redirect(auth_url)

    def post(self, request):
        authorization_code = request.data.get('code')
        if not authorization_code:
            raise ValueError("Authorization code is required")        

        token_info = exchange_code_for_token(authorization_code)
        access_token = token_info.get('access_token')

        if not access_token:
            raise ValueError("Access token is required")        

        user_info = get_user_info(access_token)        

        user = save_user_info(user_info)

        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'email': user.email,
            'message': 'User information saved successfully.'
        })