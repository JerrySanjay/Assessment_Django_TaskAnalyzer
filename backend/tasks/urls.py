from django.urls import path
from . import views

urlpatterns = [
    path('analyze/', views.analyze),
    path('suggest/', views.suggest),
    path('', views.home, name='home'),
     path('api/tasks/', views.task_list, name='task-list'),

]