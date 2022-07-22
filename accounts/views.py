
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import generics , permissions
from .serializers import *
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from django.contrib import auth
import jwt
from rest_framework.exceptions import AuthenticationFailed
from core.permissions import *
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.core.mail import EmailMessage
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


def prepare_verify_email(current_site,user,token):
    """
    Prepare verify email
    """
    relative_link = reverse('accounts:email-verify')
    absurl = 'http://'+current_site+relative_link+"?token="+str(token)
    email_body = 'Hi ' + user.name + ' Use this link to verify \n' + absurl
    data = {'email_body': email_body,
            'to_email': user.email,
            'email_subject': 'Verify Your Email'}
    return data

def verifying_user(user):
    """
    Verify user
    
    """
    if not user.is_verified:
        user.is_verified = True
        user.save()
 
def send_email(data):
    email = EmailMessage(subject=data['email_subject'],
                            body=data['email_body'], to=[data['to_email']])
    email.send()       
# Create your views here.

class VerifyEmail(APIView):
    
    token_param_config = openapi.Parameter(
        'token', in_=openapi.IN_QUERY, description='Use the token sent to user email to verify the user ',
        type=openapi.TYPE_STRING)


    # #GET 
    @swagger_auto_schema(manual_parameters=[token_param_config])
    def get(self, request):
        token = request.GET.get('token')
        try:
            #decode token to check for the user
            payload = jwt.decode(token, settings.SECRET_KEY,
                                 algorithms=["HS256"])
            
            #extracting user id from token
            user = User.objects.get(id=payload['user_id'])
            verifying_user(user)
            return Response({'email': 'Succesfully activated'},
                    status=status.HTTP_200_OK)
        except jwt.ExpiredSignatureError as identifier:
            return Response({'error': 'Activation Expired'},
                            status=status.HTTP_400_BAD_REQUEST)
        except jwt.exceptions.DecodeError as identifier:
            return Response({'error': 'Invalid Token'},
                            status=status.HTTP_400_BAD_REQUEST)


# class RegisterView(generics.GenericAPIView):
#     serializer_class = UserSerializer
#     def post(self, request):
#         '''
#         Sign UP API
#         '''

#         serializer = UserSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             #Setting email message
#             user = User.objects.get(email=request.data['email'])
#             token = RefreshToken.for_user(user).access_token
#             current_site = get_current_site(request).domain

#             email = prepare_verify_email(current_site,user,token)
            
#             #sending mail
#             send_email(email)
#             return Response(serializer.data, status=status.HTTP_201_CREATED)

#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VendorRegisterView(generics.GenericAPIView):
    serializer_class = VendorSerializer
    '''
    Sign UP for Vendor
    '''

    def post(self, request):
   
        serializer = VendorSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            #Setting email message
            user = Vendor.objects.get(user_email=request.data['email'])
            token = RefreshToken.for_user(user).access_token
            current_site = get_current_site(request).domain

            email = prepare_verify_email(current_site,user,token)
            
            #sending mail
            send_email(email)

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CustomerRegisterView(generics.GenericAPIView):
    serializer_class =CustomerSerializer

    def post(self, request):
        '''
        Sign UP for Customer
        '''

        serializer = CustomerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            #Setting email message
            user = Customer.objects.get(user_email=request.data['email'])
            token = RefreshToken.for_user(user).access_token
            current_site = get_current_site(request).domain

            email = prepare_verify_email(current_site,user,token)
            
            #sending mail
            send_email(email)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    def post(self, request):
        '''
        Login API
        '''
        data = request.data
        email = data['email']
        password = data['password']
        user = auth.authenticate(email=email, password=password)
        if not user:
            raise AuthenticationFailed('Invalid email or password.')
        if not user.is_verified:
            raise AuthenticationFailed('Email is not verified')
        if user:
            auth_token = jwt.encode(
                {'email': user.email}, settings.JWT_SECRET_KEY, algorithm="HS256")

            serializer = UserSerializer(user)

            data = {'user': serializer.data, 'token': auth_token}

            return Response(data, status=status.HTTP_200_OK)

            # SEND RES
        return Response({'detail': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
    
class ListUserAPIView(generics.ListAPIView):
    '''
    Get List of all Users
    '''
    queryset = User.objects.all()
    serializer_class = UserSerializer

class ListCustomerAPIView(generics.ListAPIView):
    '''
    Get List of all Customers
    '''

    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer

class ListVendorAPIView(generics.ListAPIView):
    '''
    Get List of all Vendors
    '''

    queryset = Vendor.objects.all()
    serializer_class = VendorSerializer
    
# class UserRetrtieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
#     '''
#     Edit , Get , Update a user with the passed id
#     '''

#     queryset = User.objects.all()
#     serializer_class = UserSerializer

class CustomerRetrtieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    '''
    Edit , Get , Update a customer with the passed id
    '''
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer


class VendorRetrtieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    '''
    Edit , Get , Update a vendor with the passed id
    '''
    queryset = Vendor.objects.all()
    serializer_class = VendorSerializer

