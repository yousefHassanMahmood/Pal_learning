from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from .models import CustomUser

def signup_view(request):
    if request.method == "POST":
        errors = CustomUser.objects.user_validator(request.POST)
        if errors:
            for msg in errors.values():
                messages.error(request, msg)
            return redirect('signup')

        user = CustomUser.objects.create_user(
            username=request.POST['email'],  
            email=request.POST['email'],
            first_name=request.POST['first_name'],
            last_name=request.POST['last_name'],
            address=request.POST['address'],
            password=request.POST['password'],
            role=request.POST.get('role', CustomUser.STUDENT)
        )
        login(request, user)
        return redirect('home')  

    return render(request, 'signup.html')


def login_view(request):
    if request.method == "POST":
        errors = CustomUser.objects.login_validator(request.POST)
        if errors:
            for msg in errors.values():
                messages.error(request, msg)
            return redirect('login')

        email = request.POST['email']
        password = request.POST['password']

        user = authenticate(request, username=email, password=password)
        if user:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Email or password incorrect.")
            return redirect('login')

    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    return redirect('login')
