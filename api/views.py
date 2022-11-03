from urllib import request
from django.http import HttpResponse
from api import serializers
from django.contrib.auth import authenticate
from api.models import User
from api.renderers import UserRenderer
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import smart_str,force_bytes,DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from  django.shortcuts import render,get_object_or_404
import requests as request_api

#Rest framework imports
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework_simplejwt.tokens import RefreshToken




# Generates Token Manually
def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }





class UserRegistration(APIView):

    permission_classes = [AllowAny]

    #Custom Json renderer 
    renderer_classes = [UserRenderer,TemplateHTMLRenderer]
    
    
    def post(self,request,format=None):
        serializer = serializers.UserRegistrationSerializer(data=request.data)

        #validate serializer
        if serializer.is_valid():

            user = serializer.save()
            #Generate tokens fo the registered user
            token = get_tokens_for_user(user=user)

            return Response({'msg':'Registration Successful','tokens':token},status=status.HTTP_201_CREATED)

        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):

    #Custom Json renderer 
    renderer_classes = [UserRenderer]
    permission_classes = [AllowAny]

    def post(self,request,format=None):
        serializer = serializers.UserLoginSerializer(data=request.data)

        #Authentication of User
        if serializer.is_valid():

            #fetch credentials
            email = serializer.data.get('email').lower()
            password = serializer.data.get('password')

            #authenticate
            user = authenticate(email=email,password=password)

            #Login
            if user is not None:

                #Generate tokens fo the Verified user
                token = get_tokens_for_user(user=user)

                return Response({'msg':'Login Successful','tokens':token},status=status.HTTP_200_OK)
            else:
                return Response({'errors':{'non_field_error':['Email or Password is not valid']}},status=status.HTTP_404_NOT_FOUND)

        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

        
class UserProfileView(APIView):

    renderer_classes = [UserRenderer]
    
    #Without permission it will not allowed anonymous user so,
    permission_classes = [IsAuthenticated]

    def get(self,request,format=None):
        
        serializer = serializers.UserProfileSerializer(request.user)
            
        return Response(serializer.data,status=status.HTTP_200_OK)


class UserChangePassword(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def post(self,request,format=None):

        serializer = serializers.UserChangePasswordSerializer(data=request.data,context={'user':request.user})
        
        if serializer.is_valid():
            return Response({'msg':'Password Change Successfully'},status=status.HTTP_200_OK)

        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
        

class SendPasswordResetEmailView(APIView):
    renderer_classes = [UserRenderer]

    def post(self,request,format=None):
        
        serializer = serializers.SendPasswordResetEmailSerializer(data=request.data)

        if serializer.is_valid():
            return Response({'msg':'Password Reset link send. Please Check your Email'},status=status.HTTP_200_OK)

        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

#Set password after change
class UserPasswordResetEmailView(APIView):
    renderer_classes = [UserRenderer]

    def post(self,request,uid,token,format=None):
        
        context_data = {'uid':uid,'token':token}
        serializer = serializers.UserPasswordResetSerializer(data=request.data,context = context_data)

        if serializer.is_valid():
            return Response({'msg':'Password Reset Successfully...'},status=status.HTTP_200_OK)

        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)