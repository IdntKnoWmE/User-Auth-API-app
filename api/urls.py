from django.urls import path,include
from api.views import SendPasswordResetEmailView, UserChangePassword, UserPasswordResetEmailView, UserProfileView, UserRegistration,LoginView
from . import views
from rest_framework_simplejwt.views import TokenObtainPairView,TokenRefreshView,TokenVerifyView




urlpatterns = [
    path('register/',UserRegistration.as_view(),name='register'),
    path('login/',LoginView.as_view(),name='login'),
    path('profile/',UserProfileView.as_view(),name='profile'),
    path('changepassword/',UserChangePassword.as_view(),name='changepassword'),
    path('send-reset-password-email/',SendPasswordResetEmailView.as_view(),name='send-reset-password-email'),
    path('reset-password/<uid>/<token>/',UserPasswordResetEmailView.as_view(),name='send-reset-password-email'),
    
    path('refreshtoken/',TokenRefreshView.as_view(),name='token_refresh'),
    path('verifytoken/',TokenVerifyView.as_view(),name='token_verify'),
    
    ]
