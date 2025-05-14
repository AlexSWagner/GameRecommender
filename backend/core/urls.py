"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from rest_framework import routers
from rest_framework.authtoken.views import obtain_auth_token

from games.views import GameViewSet, GenreViewSet, PlatformViewSet
from users.views import UserProfileViewSet
from recommendations.views import RecommendationViewSet


# API router
router = routers.DefaultRouter()
router.register(r'games', GameViewSet, basename='game')
router.register(r'genres', GenreViewSet)
router.register(r'platforms', PlatformViewSet)
router.register(r'profile', UserProfileViewSet, basename='profile')
router.register(r'recommendations', RecommendationViewSet, basename='recommendation')

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # API endpoints
    path('api/', include(router.urls)),
    
    # Authentication
    path('api/auth/', include('djoser.urls')),
    path('api/auth/', include('djoser.urls.authtoken')),  # For token-based auth
    # path('api/auth/', include('rest_framework.urls')), # djoser provides login/logout
    path('api/token/', obtain_auth_token, name='api_token'), # This might be redundant if djoser.urls.authtoken is used
    
    # Include the API docs
    path('api/docs/', include('rest_framework.urls', namespace='rest_framework')),
]
