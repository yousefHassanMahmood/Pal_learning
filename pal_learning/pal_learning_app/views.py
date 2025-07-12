import re
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from .models import CustomUser, Course, Module, Lesson
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


def home(request):
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'home.html')


def course_list(request):
    if not request.user.is_authenticated:
        return redirect('login')
    courses = Course.objects.all()
    return render(request, 'course_list.html', {'courses': courses})


def course_detail(request, course_id):
    if not request.user.is_authenticated:
        return redirect('login')
    course = get_object_or_404(Course, pk=course_id)
    modules = course.modules.all()
    return render(request, 'course_detail.html', {
        'course': course,
        'modules': modules,
    })


def module_detail(request, module_id):
    if not request.user.is_authenticated:
        return redirect('login')
    module = get_object_or_404(Module, pk=module_id)
    lessons = module.lessons.all()
    return render(request, 'module_detail.html', {
        'module': module,
        'lessons': lessons,
    })


def lesson_detail(request, lesson_id):
    if not request.user.is_authenticated:
        return redirect('login')
    lesson = get_object_or_404(Lesson, pk=lesson_id)
    return render(request, 'lesson_detail.html', {
        'lesson': lesson,
    })


def about(request):
    return render(request, 'about.html')