from django.urls import path, include
from django.contrib import admin

urlpatterns = [
    path('api/tasks/', include('tasks.urls')),
    path('admin/', admin.site.urls),
    path('', include('tasks.urls')),
]
