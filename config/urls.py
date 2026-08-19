"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from apps.accounts.views import RegisterView, LoginView, ProfileView, MeView, LogoutView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('apps.repositories.urls')),
    path('api/', include('apps.invitations.urls')),
    path('api/', include('apps.organizations.urls')),
    path('api/auth/login/', LoginView.as_view()),
    path('api/auth/register/', RegisterView.as_view()),
    path('api/users/me/', MeView.as_view()),
    path('api/users/<username>/', ProfileView.as_view()),
    path('api/auth/refresh/', TokenRefreshView.as_view()),
    path('api/auth/logout/', LogoutView.as_view()),
]
