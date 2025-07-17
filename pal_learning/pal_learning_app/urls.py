from django.urls import path
from . import views

urlpatterns = [
    # auth
    path('signup/', views.signup_view, name='signup'),
    path('login/',  views.login_view,  name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # main
    path('',       views.home,   name='home'),
    path('about/', views.about,  name='about'),

    # course flows
    path('courses/',                          views.course_list,    name='course_list'),
    path('courses/<int:course_id>/',          views.course_detail,  name='course_detail'),
    path('courses/create/',                   views.course_create,  name='course_create'),
    path('courses/<int:course_id>/edit/',     views.course_update,  name='course_update'),
    path('courses/<int:course_id>/delete/',   views.course_delete,  name='course_delete'),

    # module flows
    path('courses/<int:course_id>/modules/create/',views.module_create,name='module_create'),
    path('courses/<int:course_id>/modules/<int:module_id>/edit/',views.module_edit,name='module_edit'),
    path('courses/<int:course_id>/modules/<int:module_id>/delete/',views.module_delete,name='module_delete'),
    path('modules/<int:module_id>/',views.module_detail,name='module_detail'),
    
    
    # lesson
    path('lessons/<int:lesson_id>/',views.lesson_detail,  name='lesson_detail'),
    path('modules/<int:module_id>/lessons/create/',views.lesson_create,name='lesson_create'),
    path('lessons/<int:lesson_id>/edit/',views.lesson_edit,name='lesson_edit'),
    path('lessons/<int:lesson_id>/delete/',views.lesson_delete,name='lesson_delete'),
    path('lessons/<int:lesson_id>/',views.lesson_detail,name='lesson_detail'),    
    # quiz flows
    path('lessons/<int:lesson_id>/quiz/create/',views.quiz_create,name='quiz_create'),
    path('quizzes/<int:quiz_id>/edit/',views.quiz_edit,name='quiz_edit'),
    path('quizzes/<int:quiz_id>/delete/',views.quiz_delete,name='quiz_delete'),
    path('quizzes/<int:quiz_id>/',views.quiz_detail,name='quiz_detail'),
   # question flows
    path('quizzes/<int:quiz_id>/questions/create/',views.question_create,name='question_create'),
    path('questions/<int:question_id>/edit/',views.question_edit,name='question_edit'),
    path('questions/<int:question_id>/delete/',views.question_delete,name='question_delete'),
    # enroll
    path('courses/<int:course_id>/enroll/',views.enroll_course,name='enroll_course'),
    path('courses/<int:course_id>/drop/',views.drop_course,name='drop_course'),    
]
