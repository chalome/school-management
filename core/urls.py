from django.urls import path

from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('school-year/select/', views.select_school_year, name='select_school_year'),
    path('classrooms/', views.classroom_list, name='classroom_list'),
    path('classrooms/add/', views.classroom_create, name='classroom_create'),
    path('classrooms/<int:pk>/edit/', views.classroom_update, name='classroom_update'),
]
