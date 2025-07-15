import re
from django.conf import settings
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models

class UserManager(BaseUserManager):
    use_in_migrations = True
    
    def user_validator(self, postData):
        errors = {}
        EMAIL_REGEX = re.compile(
            r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$'
        )

        # first name
        if not postData.get('first_name'):
            errors["missing_field_first_name"] = "Please enter first name."
        elif len(postData['first_name']) < 2:
            errors["first_name_length"] = "First Name should be at least 2 characters."

        # last name
        if not postData.get('last_name'):
            errors["missing_field_last_name"] = "Please enter last name."
        elif len(postData['last_name']) < 2:
            errors["last_name_length"] = "Last Name should be at least 2 characters."

        # email
        email = postData.get('email', '').strip()
        if not email:
            errors["missing_field_email"] = "Please enter an email."
        elif not EMAIL_REGEX.match(email):
            errors['email_format'] = "Invalid email address!"
        elif self.filter(email=email).exists():
            errors['email_taken'] = "That email is already registered."

        # address
        if not postData.get('address'):
            errors["missing_field_address"] = "Please enter address."
        elif len(postData['address']) < 2:
            errors["address_length"] = "Address should be at least 2 characters."

        # password + confirm
        pwd  = postData.get('password','')
        cpwd = postData.get('confirm_pw','')
        if not (pwd and cpwd):
            errors["missing_field_password"] = "Please enter and confirm your password."
        elif len(pwd) < 8:
            errors["password_length"] = "Password should be at least 8 characters."
        elif pwd != cpwd:
            errors["password_confirm"] = "Passwords do not match."

        return errors

    def login_validator(self, postData):
        errors = {}
        if not postData.get('email') or not postData.get('password'):
            errors["login"] = "Invalid email or password."
        return errors
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, username=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('role', CustomUser.ADMIN)
        extra_fields.setdefault('is_approved', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('role') != CustomUser.ADMIN:
            raise ValueError('Superuser must have role=ADMIN.')
        return self.create_user(email, password, **extra_fields)
class CustomUser(AbstractUser):
    STUDENT    = 'student'
    INSTRUCTOR = 'instructor'
    ADMIN      = 'admin'
    ROLE_CHOICES = [
        (STUDENT,    'Student'),
        (INSTRUCTOR, 'Instructor'),
        (ADMIN,      'Admin'),
    ]

    objects = UserManager()

    email        = models.EmailField('email address', unique=True)
    role         = models.CharField(max_length=20, choices=ROLE_CHOICES, default=STUDENT)
    address      = models.CharField(max_length=255, blank=True)
    is_approved  = models.BooleanField(default=False)
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def save(self, *args, **kwargs):
        # auto-approve non-instructors
        if self.role != CustomUser.INSTRUCTOR:
            self.is_approved = True
            self.is_active   = True
        else:
            # instructors must be approved manually
            self.is_active = self.is_approved

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.email} ({self.role})"
class Course(models.Model):
    BEGINNER     = 'beginner'
    INTERMEDIATE = 'intermediate'
    ADVANCED     = 'advanced'
    DIFFICULTY_CHOICES = [
        (BEGINNER,     'Beginner'),
        (INTERMEDIATE, 'Intermediate'),
        (ADVANCED,     'Advanced'),
    ]

    title        = models.CharField(max_length=255)
    description  = models.TextField(blank=True)
    topic        = models.CharField(max_length=100, blank=True)
    difficulty   = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default=BEGINNER)
    instructor   = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='courses_taught')
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Module(models.Model):
    course     = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='modules')
    title      = models.CharField(max_length=255)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['sort_order']

    def __str__(self):
        return f"{self.course.title} — {self.title}"


class Lesson(models.Model):
    VIDEO = 'video'
    TEXT  = 'text'
    CONTENT_TYPE_CHOICES = [(VIDEO, 'Video'), (TEXT, 'Text')]

    module       = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='lessons')
    title        = models.CharField(max_length=255)
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPE_CHOICES, default=TEXT)
    content_url  = models.URLField(max_length=500, blank=True)
    body         = models.TextField(blank=True)
    sort_order   = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['sort_order']

    def __str__(self):
        return f"{self.module.title} — {self.title}"


class Quiz(models.Model):
    lesson = models.OneToOneField(Lesson, on_delete=models.CASCADE, related_name='quiz')
    title  = models.CharField(max_length=255)

    def __str__(self):
        return f"Quiz: {self.title}"


class Question(models.Model):
    SINGLE = 'single_choice'
    MULTI  = 'multiple_choice'
    QUESTION_TYPE_CHOICES = [(SINGLE, 'Single Choice'), (MULTI, 'Multiple Choice')]

    quiz          = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    text          = models.TextField()
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPE_CHOICES, default=SINGLE)

    def __str__(self):
        return self.text[:50]


class Choice(models.Model):
    question   = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    text       = models.CharField(max_length=500)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.text} ({'✓' if self.is_correct else '✗'})"


class Enrollment(models.Model):
    IN_PROGRESS = 'in_progress'
    COMPLETED   = 'completed'
    DROPPED     = 'dropped'
    STATUS_CHOICES = [
        (IN_PROGRESS, 'In Progress'),
        (COMPLETED,   'Completed'),
        (DROPPED,     'Dropped'),
    ]

    student     = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='enrollments')
    course      = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    enrolled_at = models.DateTimeField(auto_now_add=True)
    status      = models.CharField(max_length=20, choices=STATUS_CHOICES, default=IN_PROGRESS)

    class Meta:
        unique_together = ('student', 'course')

    def __str__(self):
        return f"{self.student} → {self.course}"


class Progress(models.Model):
    student     = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='progress_records')
    lesson      = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='progress_records')
    started_at  = models.DateTimeField(auto_now_add=True)
    completed_at= models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('student', 'lesson')

    def __str__(self):
        return f"{self.student} — {self.lesson}"


class QuizSubmission(models.Model):
    student      = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='quiz_submissions')
    quiz         = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='submissions')
    submitted_at = models.DateTimeField(auto_now_add=True)
    score        = models.DecimalField(max_digits=5, decimal_places=2)

    class Meta:
        unique_together = ('student', 'quiz')

    def __str__(self):
        return f"{self.student} scored {self.score} on {self.quiz}"


class DiscussionThread(models.Model):
    lesson     = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='threads')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='threads_created')
    title      = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Comment(models.Model):
    thread     = models.ForeignKey(DiscussionThread, on_delete=models.CASCADE, related_name='comments')
    user       = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comments')
    body       = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user}: {self.body[:30]}"
