import re

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

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

        user = authenticate(
            request,
            username=request.POST['email'],
            password=request.POST['password']
        )
        if user:
            login(request, user)
            return redirect('home')

        messages.error(request, "Email or password incorrect.")
        return redirect('login')

    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def home(request):
    return render(request, 'home.html')


@login_required
def course_list(request):
    courses = Course.objects.all()
    return render(request, 'course_list.html', {'courses': courses})


@login_required
def course_detail(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    modules = course.modules.all()
    return render(request, 'course_detail.html', {
        'course': course,
        'modules': modules,
    })


@login_required
def module_detail(request, module_id):
    module = get_object_or_404(Module, pk=module_id)
    lessons = module.lessons.all()
    return render(request, 'module_detail.html', {
        'module': module,
        'lessons': lessons,
    })


@login_required
def lesson_detail(request, lesson_id):
    lesson = get_object_or_404(Lesson, pk=lesson_id)
    return render(request, 'lesson_detail.html', {
        'lesson': lesson,
    })


def about(request):
    return render(request, 'about.html')
