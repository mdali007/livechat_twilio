from django.contrib import admin
from django.urls import path, include  # Import 'include'
from chat import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('chat/', include('chat.urls')),  # Include chat app URLs
    path('accounts/', include('accounts.urls')),  # Include accounts app URLs
    path("", views.chat_home, name="chat_home"),  # Home page
]
