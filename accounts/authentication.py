from .models import User
import jwt
from rest_framework import authentication, exceptions
from django.conf import settings
from rest_framework.response import Response


class JWTAuthentication(authentication.BaseAuthentication):

    def authenticate(self, request):
        auth_data = authentication.get_authorization_header(request)

        if not auth_data:
            return None

        try:
            _, token = auth_data.decode('utf-8').split(' ')
        except:
            raise exceptions.AuthenticationFailed(
                'Please insert \'Bearer\' before the inserted token.')
            
        try:
            payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms="HS256")

            user = User.objects.get(email=payload['email'])
            return (user, token)

        except jwt.DecodeError as identifier:
            raise exceptions.AuthenticationFailed(
                'Your token is invalid,login')
        except jwt.ExpiredSignatureError as identifier:
            raise exceptions.AuthenticationFailed(
                'Your token is expired,login')
