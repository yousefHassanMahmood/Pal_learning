from django.contrib import admin
from .models import (
    CustomUser, Course, Module, Lesson, Quiz, Question, Choice,
    Enrollment, Progress, QuizSubmission, DiscussionThread, Comment
)

# 1) Admin action to approve instructors
@admin.action(description="Approve selected instructors")
def approve_instructors(modeladmin, request, queryset):
    to_approve = queryset.filter(role=CustomUser.INSTRUCTOR, is_approved=False)
    count = to_approve.update(is_approved=True, is_active=True)
    modeladmin.message_user(request, f"{count} instructor account(s) approved.")

# 2) CustomUser admin
@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display   = ('username', 'email', 'role', 'is_approved', 'is_active', 'date_joined')
    list_filter    = ('role', 'is_approved', 'is_active')
    search_fields  = ('username', 'email')
    actions        = [approve_instructors]

# Inlines for nested editing
class ModuleInline(admin.TabularInline):
    model = Module
    extra = 1

class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1

# 3) Course admin
@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display   = ('title', 'instructor', 'difficulty', 'created_at')
    list_filter    = ('difficulty', 'instructor')
    search_fields  = ('title', 'topic')
    inlines        = [ModuleInline]

# 4) Module admin
@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display   = ('title', 'course', 'sort_order')
    list_filter    = ('course',)
    inlines        = [LessonInline]

# 5) Lesson admin
@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display   = ('title', 'module', 'content_type', 'sort_order')
    list_filter    = ('content_type', 'module')
    search_fields  = ('title', 'body')

# 6) Quiz + related
@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display  = ('title', 'lesson')
    list_filter   = ('lesson',)
    search_fields = ('title',)

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display  = ('text', 'quiz', 'question_type')
    list_filter   = ('question_type', 'quiz')
    search_fields = ('text',)

@admin.register(Choice)
class ChoiceAdmin(admin.ModelAdmin):
    list_display  = ('text', 'question', 'is_correct')
    list_filter   = ('is_correct', 'question')
    search_fields = ('text',)

# 7) Enrollments & progress
@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display  = ('student', 'course', 'status', 'enrolled_at')
    list_filter   = ('status', 'course')
    search_fields = ('student__username', 'course__title')

@admin.register(Progress)
class ProgressAdmin(admin.ModelAdmin):
    list_display  = ('student', 'lesson', 'started_at', 'completed_at')
    list_filter   = ('student', 'lesson')

@admin.register(QuizSubmission)
class QuizSubmissionAdmin(admin.ModelAdmin):
    list_display  = ('student', 'quiz', 'score', 'submitted_at')
    list_filter   = ('quiz', 'student')

# 8) Discussion forum
@admin.register(DiscussionThread)
class DiscussionThreadAdmin(admin.ModelAdmin):
    list_display  = ('title', 'lesson', 'created_by', 'created_at')
    list_filter   = ('lesson', 'created_by')

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display  = ('user', 'thread', 'body', 'created_at')
    list_filter   = ('thread', 'user')
    search_fields = ('body',)
