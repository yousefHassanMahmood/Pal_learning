from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from .models import CustomUser, Course, Module, Lesson
from .forms import CourseForm
from .utils import is_instructor_or_admin


def signup_view(request):
    if request.method == "POST":
        errors = CustomUser.objects.user_validator(request.POST)
        if errors:
            for msg in errors.values():
                messages.error(request, msg)
            return redirect('signup')

        email   = request.POST['email']
        password = request.POST['password']
        user = CustomUser.objects.create_user(
            email=email,
            password=password,
            first_name=request.POST['first_name'],
            last_name=request.POST['last_name'],
            address=request.POST['address'],
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
            # If the user is staff/superuser, send them to the Django admin:
            if user.is_staff or user.is_superuser:
                return redirect(reverse('admin:index'))
            # Otherwise, normal home
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


@login_required
@user_passes_test(is_instructor_or_admin)
def course_create(request):
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save(commit=False)
            # assign the current instructor (unless superuser who could pick someone else)
            if not request.user.is_superuser:
                course.instructor = request.user
            course.save()
            messages.success(request, "Course created successfully.")
            return redirect('course_detail', course_id=course.pk)
    else:
        form = CourseForm()
    return render(request, 'course_form.html', {'form': form})


@login_required
@user_passes_test(is_instructor_or_admin)
def course_update(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    # instructors can only edit their own courses
    if not request.user.is_superuser and course.instructor != request.user:
        messages.error(request, "You don’t have permission to edit this course.")
        return redirect('course_detail', course_id=course.pk)

    if request.method == 'POST':
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, "Course updated successfully.")
            return redirect('course_detail', course_id=course.pk)
    else:
        form = CourseForm(instance=course)

    return render(request, 'course_form.html', {
        'form': form,
        'course': course,
    })


@login_required
@user_passes_test(is_instructor_or_admin)
def course_delete(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    if not request.user.is_superuser and course.instructor != request.user:
        messages.error(request, "You don’t have permission to delete this course.")
        return redirect('course_detail', course_id=course.pk)

    if request.method == 'POST':
        course.delete()
        messages.success(request, "Course deleted.")
        return redirect('course_list')

    return render(request, 'course_confirm_delete.html', {
        'course': course
    })