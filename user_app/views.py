
import email
from os import access
import re
from django.shortcuts import render,redirect
import requests as api_req
import json
from django.contrib import messages
from django.contrib.sessions.models import Session
import time

# Create your views here.


def handle_session(request):
    if 'member' not in request.session:
        messages.error(request,'Please Login')
        return False
    
    
    active_time  = (time.time() - request.session['member']['login_time'])//60
    #print(active_time)
    
    if active_time >= 60:
        del request.session['member']
        messages.error(request,'Please Login again..')
        return False
    elif active_time < 60 and active_time >= 50:

        refresh_token = request.session['member']['refresh_token']

        api_data = {
            "refresh":refresh_token
        }

        headers_data = {
            "Accept":"application/json"
        }


        response = api_req.post("http://127.0.0.1:8000/user_api/refreshtoken/",headers=headers_data,data=api_data)
        
        #print(refresh_token)
        #print(response.status_code,response.json())

        if response.status_code == 200:
        
            request.session['member']['access_token'] = response.json()['access']
            request.session['member']['refresh_token'] = response.json()['refresh']
            request.session['member']['login_time'] = time.time()
            request.session.modified = True
        
        else:
            messages.error(request,response.json()['errors'])
            return False

        

    return True

    


def register(request):

    if request.method=="POST":

        first_name = request.POST['fname'].capitalize()
        last_name = request.POST['lname'].capitalize()
        email = request.POST['email'].lower()
        password = request.POST['password']

        api_data = {
            "email":email,
            "first_name":first_name,
            "last_name":last_name,
            "password":password
        }
        
        print(api_data)
        response = api_req.post("http://127.0.0.1:8000/user_api/register/",data=api_data)

        if response.status_code == 201:

            messages.info(request,'Account created successfully')
            return redirect('login')
        
        else:

            messages.error(request,response.json()['errors'])
            
        


    return render(request,'user_app/Register.html')


def login(request):

    if request.method == "POST":

        email = request.POST['email'].lower()
        password = request.POST['password']

        api_data = {
            "email":email,
            "password":password
        }

        response = api_req.post("http://127.0.0.1:8000/user_api/login/",data=api_data)

        if response.status_code == 200:
            
            access_token = 'Bearer ' + response.json()['tokens']['access']

            user_responsed = api_req.get("http://127.0.0.1:8000/user_api/profile/",headers={'Authorization':access_token})

            user = user_responsed.json()

            if 'member' in request.session:
                del request.session['member']

            request.session['member'] = {
                'id' : user['id'],
                'first_name' : user['first_name'],
                'last_name' : user['last_name'],
                'access_token' : response.json()['tokens']['access'],
                'refresh_token' : response.json()['tokens']['refresh'],
                'login_time' : time.time()
            }

            
            messages.info(request,'Login Successful')
            return redirect('homepage')
        else:
            messages.error(request,response.json()['errors'])
        
    return render(request,'user_app/Login.html')


def homepage(request):
    
    if not handle_session(request):
        return redirect('login')

    

    return render(request,'user_app/Homepage.html')


def logout(request):
    if 'member' not in request.session:
        messages.error(request,'Please Login')  
    else:
        del request.session['member']
        messages.info(request,'Successfully logged out')
    
    return redirect('login')


def change_password(request):
    
    if not handle_session(request):
        return redirect('login')

    if request.method == 'POST':
        password = request.POST.get('password')
        password2 = request.POST.get('password2')

        access_token = request.session['member']['access_token']
        api_data = {
            "password":password,
            "password2":password2
        }

        headers_data = {
            "Accept":"application/json",
            "Authorization": "Bearer "+ access_token
        }

        response = api_req.post("http://127.0.0.1:8000/user_api/changepassword/",headers=headers_data,data=api_data)

        print(response.json())
        
        if response.status_code==200:
            
            del request.session['member']
            messages.info(request,'Your Password Changed Successfully. Please log in agin!')
            return redirect('login')
        
        else:
            del request.session['member']
            messages.error(request,'Some error is caused. Please login again..')
            return redirect('login')



    
    return render(request,'user_app/Change_Password.html')