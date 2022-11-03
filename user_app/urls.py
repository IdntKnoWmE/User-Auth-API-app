
from django.urls import path,include
from user_app import views




urlpatterns = [
    path('login/',views.login,name='login'),
    path('register',views.register,name='register'),
    path('logout',views.logout,name='logout'),
    path('homepage',views.homepage,name='homepage'),
    path('change_password/',views.change_password,name='change_password'),
    ]
