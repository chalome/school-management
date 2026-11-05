from django.urls import path

from . import views

urlpatterns = [
    path('', views.child_list, name='child_list'),
    path('add/', views.child_create, name='child_create'),
    path('<int:pk>/', views.child_detail, name='child_detail'),
    path('<int:pk>/edit/', views.child_update, name='child_update'),
]
