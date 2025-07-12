from django.urls import path
from . import views

urlpatterns = [
    # auth
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # main
    path('',                 views.home,           name='home'),
    path('about/',           views.about,          name='about'),

    # course flows
    path('courses/',         views.course_list,    name='course_list'),
    path('courses/<int:course_id>/', views.course_detail, name='course_detail'),
    path('modules/<int:module_id>/', views.module_detail, name='module_detail'),
    path('lessons/<int:lesson_id>/', views.lesson_detail, name='lesson_detail'),
]
