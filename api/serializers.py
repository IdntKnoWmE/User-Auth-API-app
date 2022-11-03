from urllib import request
from rest_framework import serializers
from api.email_utils import Util
from api.models import User

#lib for reset email 
from django.utils.encoding import smart_str,force_bytes,DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.sites.shortcuts import get_current_site

def strong_password_validator(password):
    """
    Conditions for a valid password are:

        Should have at least one number.
        Should have at least one uppercase and one lowercase character.
        Should have at least one special symbol : '$', '@', '#', '%'.
        Should be between 6 to 20 characters long.
    """
    SpecialSym =['$', '@', '#', '%']
    val = True
      
    if len(password) < 6:
        print('length should be at least 6')
        val = False
          
    if len(password) > 20:
        print('length should be not be greater than 8')
        val = False
          
    if not any(char.isdigit() for char in password):
        print('Password should have at least one numeral')
        val = False
          
    if not any(char.isupper() for char in password):
        print('Password should have at least one uppercase letter')
        val = False
    if not any(char.islower() for char in password):
        print('Password should have at least one lowercase letter')
        val = False
          
    if not any(char in SpecialSym for char in password):
        print('Password should have at least one of the symbols $@#')
        val = False
    
    return val
    

def Send_Reset_Email_Link(user):

    #generate UID
    uid = urlsafe_base64_encode(force_bytes(user.id)) #force byte is used bec urlsafe encode takes only bytes
    print('Encode UID: ',uid)

    #Gen Token
    token = PasswordResetTokenGenerator().make_token(user)
    print('Password Reset Token: ', token)

    site = "http://127.0.0.1:8000/" #add your domain name here
    link = site + uid + '/' + token
    print('Password Reset Link:', link)

    #Sent Email
    email_body = 'Please Click the Link to Reset your Password ' + link

    email_data = {
        "email_subject":'Reset Password Link',
        "email_body": email_body,
        'to_email': user.email
    }

    #Util.send_email(email_data)

    return link

class UserRegistrationSerializer(serializers.ModelSerializer):


    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'password']
        extra_kwargs = {
            'password': {'write_only':True}
        }
    #Validate password
    def validate(self, attrs):
        password = attrs.get('password')
        
        if strong_password_validator(password = password)==False:
            raise serializers.ValidationError("Passwords is not strong...")
        return attrs

    #create user
    def create(self, validate_data):
        return User.objects.create_user(**validate_data)


class UserLoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=40)
    class Meta:
        model = User
        fields = ['email','password']


class UserProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['id','first_name','last_name','email','password']


class UserChangePasswordSerializer(serializers.Serializer):
    
    password = serializers.CharField(max_length=255,style={'input_type':'password'},write_only=True)
    password2 = serializers.CharField(max_length=255,style={'input_type':'password'},write_only=True)

    class Meta:
        fields = ['password','password2']
    
    def validate(self,attrs):
        password = attrs.get('password')
        password2 = attrs.get('password2')

        user = self.context.get('user')#fetch from context dictionary

        if password!=password2:
            raise serializers.ValidationError("Passwords not matched")

        if strong_password_validator(password = password)==False:
            raise serializers.ValidationError("Passwords is not strong...")

        user.set_password(password)
        user.save()

        return attrs


class SendPasswordResetEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length = 40)

    class Meta:
        fields = ['email']

    def validate(self, attrs):
        email = attrs.get('email')

        if User.objects.filter(email=email).exists():

            user = User.objects.get(email=email)
            Link = Send_Reset_Email_Link(user=user)

            return attrs

        else:
            raise serializers.ValidationError("You are not a registered User...")


class UserPasswordResetSerializer(serializers.Serializer):

    password = serializers.CharField(max_length=255,style={'input_type':'password'},write_only=True)
    password2 = serializers.CharField(max_length=255,style={'input_type':'password'},write_only=True)

    class Meta:
        fields = ['password','password2']
    
    def validate(self,attrs):
        try:
            password = attrs.get('password')
            password2 = attrs.get('password2')

            #fetch from context dictionary
            uid = self.context.get('uid')
            token = self.context.get('token')

            if password!=password2:
                raise serializers.ValidationError("Passwords not matched")

            if strong_password_validator(password = password)==False:
                raise serializers.ValidationError("Passwords is not strong...")

            #fetch uid
            user_id = smart_str(urlsafe_base64_decode(uid)) #smart str will retur string of bytes uid
            user = User.objects.get(id=user_id)

            #check User
            if user is None:
                raise serializers.ValidationError("User not Exist...")
            
            #check token
            if not PasswordResetTokenGenerator().check_token(user,token):
                raise serializers.ValidationError("Token is not Valid or Expired...")


            user.set_password(password)
            user.save()

            return attrs
        except DjangoUnicodeDecodeError as identifier:

            PasswordResetTokenGenerator().check_token(user,token)
            raise serializers.ValidationError("Token is not Valid or Expired...")
