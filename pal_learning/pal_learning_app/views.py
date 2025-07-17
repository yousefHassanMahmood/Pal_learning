from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from .models import CustomUser, Course, Module, Lesson,Quiz,QuizSubmission,Question,Enrollment
from .forms import CourseForm,ModuleForm,LessonForm,QuizForm,QuestionForm, ChoiceFormSet
from .utils import is_instructor_or_admin

from urllib.parse import urlparse, parse_qs
import random
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
    user = request.user

    if user.role == CustomUser.STUDENT:
        # only grab in-progress enrollments
        enrollments = (
            user.enrollments
                .select_related('course')
                .filter(status=Enrollment.IN_PROGRESS)
        )
        context = {
            'is_student':   True,
            'enrollments':  enrollments,
        }
    else:
        # instructors/admins see their own courses
        courses_taught = user.courses_taught.all()
        context = {
            'is_student':      False,
            'courses_taught':  courses_taught,
        }

    return render(request, 'home.html', context)


@login_required
def course_list(request):
    q = request.GET.get('q', '').strip()
    courses = Course.objects.all()
    if q:
        courses = (
            courses.filter(title__icontains=q)
                   .union(courses.filter(topic__icontains=q))
        )

    for course in courses:
        # Active enrollment?
        course.is_enrolled = Enrollment.objects.filter(
            student=request.user,
            course=course,
            status=Enrollment.IN_PROGRESS
        ).exists()
        # Dropped previously?
        course.is_dropped = Enrollment.objects.filter(
            student=request.user,
            course=course,
            status=Enrollment.DROPPED
        ).exists()

    return render(request, 'course_list.html', {
        'courses': courses,
        'query':   q,
    })


@login_required
def course_detail(request, course_id):
    course  = get_object_or_404(Course, pk=course_id)
    modules = course.modules.all()

    enrollment = None
    # only students can enroll/drop
    if request.user.role == CustomUser.STUDENT:
        enrollment = Enrollment.objects.filter(
            student=request.user,
            course=course
        ).first()

    return render(request, 'course_detail.html', {
        'course'     : course,
        'modules'    : modules,
        'enrollment' : enrollment,
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

    embed_url = None
    if lesson.content_type == 'video' and lesson.content_url:
        parsed = urlparse(lesson.content_url)
        # Case A: standard YouTube watch?v=ID
        if 'youtube.com' in parsed.netloc:
            q = parse_qs(parsed.query)
            vid = q.get('v', [None])[0]
            if vid:
                embed_url = f'https://www.youtube.com/embed/{vid}'
        # Case B: youtu.be short link
        elif 'youtu.be' in parsed.netloc:
            vid = parsed.path.lstrip('/')
            embed_url = f'https://www.youtube.com/embed/{vid}'

    return render(request, 'lesson_detail.html', {
        'lesson': lesson,
        'embed_url': embed_url,
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
    # only allow POST
    if request.method != 'POST':
        return redirect('course_detail', course_id=course_id)

    course = get_object_or_404(Course, pk=course_id)
    if not request.user.is_superuser and course.instructor != request.user:
        messages.error(request, "You don’t have permission to delete this course.")
        return redirect('course_detail', course_id=course_id)

    course.delete()
    messages.success(request, "Course deleted successfully.")
    return redirect('course_list')
    
@login_required
@user_passes_test(is_instructor_or_admin)
def module_create(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    # Only the course’s instructor (or superuser) may add modules
    if not request.user.is_superuser and course.instructor != request.user:
        messages.error(request, "You don’t have permission to add modules here.")
        return redirect('course_detail', course_id=course_id)

    if request.method == 'POST':
        form = ModuleForm(request.POST)
        if form.is_valid():
            module = form.save(commit=False)
            module.course = course
            module.save()
            messages.success(request, "Module created successfully.")
            return redirect('course_detail', course_id=course_id)
    else:
        form = ModuleForm()

    return render(request, 'module_form.html', {
        'form': form,
        'course': course,
    })


@login_required
@user_passes_test(is_instructor_or_admin)
def module_edit(request, course_id, module_id):
    course = get_object_or_404(Course, pk=course_id)
    module = get_object_or_404(Module, pk=module_id, course=course)
    # Only the course’s instructor (or superuser) may edit
    if not request.user.is_superuser and course.instructor != request.user:
        messages.error(request, "You don’t have permission to edit this module.")
        return redirect('course_detail', course_id=course_id)

    if request.method == 'POST':
        form = ModuleForm(request.POST, instance=module)
        if form.is_valid():
            form.save()
            messages.success(request, "Module updated successfully.")
            return redirect('course_detail', course_id=course_id)
    else:
        form = ModuleForm(instance=module)

    return render(request, 'module_form.html', {
        'form': form,
        'course': course,
        'module': module,
    })


@login_required
@user_passes_test(is_instructor_or_admin)
def module_delete(request, course_id, module_id):
    # Only accept POST
    if request.method != 'POST':
        return redirect('course_detail', course_id=course_id)

    course = get_object_or_404(Course, pk=course_id)
    module = get_object_or_404(Module, pk=module_id, course=course)
    # Permission check
    if not request.user.is_superuser and course.instructor != request.user:
        messages.error(request, "You don’t have permission to delete this module.")
        return redirect('course_detail', course_id=course_id)

    module.delete()
    messages.success(request, "Module deleted.")
    return redirect('course_detail', course_id=course_id)

@login_required
@user_passes_test(is_instructor_or_admin)
def lesson_create(request, module_id):
    module = get_object_or_404(Module, pk=module_id)
    # only instructor or admin may add lessons
    if not request.user.is_superuser and module.course.instructor != request.user:
        messages.error(request, "You don’t have permission to add lessons here.")
        return redirect('module_detail', module_id=module_id)

    if request.method == 'POST':
        form = LessonForm(request.POST)
        if form.is_valid():
            lesson = form.save(commit=False)
            lesson.module = module
            lesson.save()
            messages.success(request, "Lesson created successfully.")
            return redirect('module_detail', module_id=module_id)
    else:
        form = LessonForm()

    return render(request, 'lesson_form.html', {
        'form': form,
        'module': module,
    })
    
@login_required
@user_passes_test(is_instructor_or_admin)
def lesson_edit(request, lesson_id):
    lesson = get_object_or_404(Lesson, pk=lesson_id)
    course = lesson.module.course
    # Only the course’s instructor (or superuser) may edit
    if not request.user.is_superuser and course.instructor != request.user:
        messages.error(request, "You don’t have permission to edit this lesson.")
        return redirect('lesson_detail', lesson_id=lesson_id)

    if request.method == 'POST':
        form = LessonForm(request.POST, instance=lesson)
        if form.is_valid():
            form.save()
            messages.success(request, "Lesson updated successfully.")
            return redirect('lesson_detail', lesson_id=lesson_id)
    else:
        form = LessonForm(instance=lesson)

    return render(request, 'lesson_form.html', {
        'form': form,
        'lesson': lesson,
    })


@login_required
@user_passes_test(is_instructor_or_admin)
def lesson_delete(request, lesson_id):
    # Only accept POST
    if request.method != 'POST':
        return redirect('lesson_detail', lesson_id=lesson_id)

    lesson = get_object_or_404(Lesson, pk=lesson_id)
    course = lesson.module.course
    # Only the course’s instructor (or superuser) may delete
    if not request.user.is_superuser and course.instructor != request.user:
        messages.error(request, "You don’t have permission to delete this lesson.")
        return redirect('lesson_detail', lesson_id=lesson_id)

    module_id = lesson.module.id
    lesson.delete()
    messages.success(request, "Lesson deleted.")
    return redirect('module_detail', module_id=module_id)

@login_required
@user_passes_test(is_instructor_or_admin)
def quiz_create(request, lesson_id):
    lesson = get_object_or_404(Lesson, pk=lesson_id)
    course = lesson.module.course
    if not request.user.is_superuser and course.instructor != request.user:
        messages.error(request, "You don’t have permission to add a quiz here.")
        return redirect('module_detail', module_id=lesson.module.id)

    if request.method == 'POST':
        form = QuizForm(request.POST)
        if form.is_valid():
            quiz = form.save(commit=False)
            quiz.lesson = lesson
            quiz.save()
            messages.success(request, "Quiz created.")
            return redirect('quiz_detail', quiz_id=quiz.id)
    else:
        form = QuizForm()

    return render(request, 'quiz_form.html', {
        'form': form,
        'lesson': lesson,
    })

@login_required
@user_passes_test(is_instructor_or_admin)
def quiz_edit(request, quiz_id):
    quiz = get_object_or_404(Quiz, pk=quiz_id)
    course = quiz.lesson.module.course
    if not request.user.is_superuser and course.instructor != request.user:
        messages.error(request, "You don’t have permission to edit this quiz.")
        return redirect('lesson_detail', lesson_id=quiz.lesson.id)

    if request.method == 'POST':
        form = QuizForm(request.POST, instance=quiz)
        if form.is_valid():
            form.save()
            messages.success(request, "Quiz updated.")
            return redirect('quiz_detail', quiz_id=quiz.id)
    else:
        form = QuizForm(instance=quiz)

    return render(request, 'quiz_form.html', {
        'form': form,
        'quiz': quiz,
    })


@login_required
@user_passes_test(is_instructor_or_admin)
def quiz_delete(request, quiz_id):
    # only accept POST
    if request.method != 'POST':
        return redirect('quiz_detail', quiz_id=quiz_id)

    quiz = get_object_or_404(Quiz, pk=quiz_id)
    course = quiz.lesson.module.course
    if not request.user.is_superuser and course.instructor != request.user:
        messages.error(request, "You don’t have permission to delete this quiz.")
        return redirect('quiz_detail', quiz_id=quiz_id)

    lesson_id = quiz.lesson.id
    quiz.delete()
    messages.success(request, "Quiz deleted.")
    return redirect('lesson_detail', lesson_id=lesson_id)



@login_required
def quiz_detail(request, quiz_id):
    quiz = get_object_or_404(Quiz, pk=quiz_id)
    user = request.user
    course = quiz.lesson.module.course
    is_instructor = user.is_superuser or course.instructor == user

    # Instructor sees static overview
    if is_instructor:
        return render(request, 'quiz_detail.html', {
            'quiz': quiz,
            'is_instructor': True,
        })

    # STUDENT FLOW
    if request.method == 'POST':
        # grading logic unchanged…
        total = quiz.questions.count()
        correct_count = 0
        for question in quiz.questions.all():
            selected_ids = set(map(int, request.POST.getlist(f'question_{question.id}')))
            correct_ids  = set(question.choices.filter(is_correct=True)
                                             .values_list('id', flat=True))
            if question.question_type == Question.SINGLE:
                if len(selected_ids) == 1 and selected_ids <= correct_ids:
                    correct_count += 1
            else:
                if selected_ids == correct_ids:
                    correct_count += 1

        score = round((correct_count / total) * 100, 2) if total else 0
        QuizSubmission.objects.update_or_create(
            student=user,
            quiz=quiz,
            defaults={'score': score}
        )
        return render(request, 'quiz_detail.html', {
            'quiz': quiz,
            'is_instructor': False,
            'submitted': True,
            'score': score,
            'total': total,
        })

    # GET: prepare shuffled questions & choices
    questions = list(quiz.questions.prefetch_related('choices').all())
    for q in questions:
        choices = list(q.choices.all())
        random.shuffle(choices)
        q.choices_shuffled = choices

    return render(request, 'quiz_detail.html', {
        'quiz': quiz,
        'is_instructor': False,
        'submitted': False,
        'questions': questions,
    })
@login_required
@user_passes_test(is_instructor_or_admin)
def question_create(request, quiz_id):
    quiz = get_object_or_404(Quiz, pk=quiz_id)
    course = quiz.lesson.module.course
    if not request.user.is_superuser and course.instructor != request.user:
        messages.error(request, "You don’t have permission to add questions here.")
        return redirect('quiz_detail', quiz_id=quiz_id)

    if request.method == 'POST':
        q_form = QuestionForm(request.POST)
        if q_form.is_valid():
            question = q_form.save(commit=False)
            question.quiz = quiz
            question.save()

            formset = ChoiceFormSet(request.POST, instance=question)
            if formset.is_valid():
                formset.save()
                messages.success(request, "Question and choices saved.")
                return redirect('quiz_detail', quiz_id=quiz_id)
        else:
            formset = ChoiceFormSet(request.POST)
    else:
        q_form = QuestionForm()
        formset = ChoiceFormSet()

    return render(request, 'question_form.html', {
        'quiz': quiz,
        'q_form': q_form,
        'formset': formset,
    })
    
@login_required
@user_passes_test(is_instructor_or_admin)
def question_edit(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    quiz = question.quiz
    course = quiz.lesson.module.course
    if not request.user.is_superuser and course.instructor != request.user:
        messages.error(request, "You don’t have permission to edit this question.")
        return redirect('quiz_detail', quiz_id=quiz.id)

    if request.method == 'POST':
        q_form = QuestionForm(request.POST, instance=question)
        formset = ChoiceFormSet(request.POST, instance=question)
        if q_form.is_valid() and formset.is_valid():
            q_form.save()
            formset.save()
            messages.success(request, "Question updated.")
            return redirect('quiz_detail', quiz_id=quiz.id)
    else:
        q_form = QuestionForm(instance=question)
        formset = ChoiceFormSet(instance=question)

    return render(request, 'question_form.html', {
        'quiz': quiz,
        'q_form': q_form,
        'formset': formset,
        'question': question,
    })


@login_required
@user_passes_test(is_instructor_or_admin)
def question_delete(request, question_id):
    # only accept POST
    if request.method != 'POST':
        return redirect('quiz_detail', quiz_id=Quiz.objects.get(questions__id=question_id).id)

    question = get_object_or_404(Question, pk=question_id)
    quiz = question.quiz
    course = quiz.lesson.module.course
    if not request.user.is_superuser and course.instructor != request.user:
        messages.error(request, "You don’t have permission to delete this question.")
        return redirect('quiz_detail', quiz_id=quiz.id)

    question.delete()
    messages.success(request, "Question deleted.")
    return redirect('quiz_detail', quiz_id=quiz.id)

@login_required
def enroll_course(request, course_id):
    course = get_object_or_404(Course, pk=course_id)

    # Only students can enroll
    if request.user.role != 'student':
        messages.error(request, "Only students can enroll in courses.")
        return redirect('course_detail', course_id=course_id)

    # Fetch or create the enrollment record
    enrollment, created = Enrollment.objects.get_or_create(
        student=request.user,
        course=course,
        defaults={'status': Enrollment.IN_PROGRESS}
    )

    if not created:
        # if it existed, reset status to in_progress
        enrollment.status = Enrollment.IN_PROGRESS
        enrollment.save()
        messages.success(request, f"You’ve re-enrolled in “{course.title}”.")
    else:
        messages.success(request, f"You’ve been enrolled in “{course.title}”!")

    return redirect('course_detail', course_id=course_id)

@login_required
def drop_course(request, course_id):
    # only POSTs allowed
    if request.method != 'POST':
        return redirect('course_detail', course_id=course_id)

    course = get_object_or_404(Course, pk=course_id)
    enrollment = Enrollment.objects.filter(
        student=request.user,
        course=course,
        status=Enrollment.IN_PROGRESS
    ).first()

    if not enrollment:
        messages.error(request, "You’re not currently enrolled in that course.")
        return redirect('course_detail', course_id=course_id)

    # mark dropped
    enrollment.status = Enrollment.DROPPED
    enrollment.save()

    messages.success(request, f"You’ve dropped “{course.title}”.")
    return redirect('course_list')

