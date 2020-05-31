"""sharinator URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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
from django.urls import path

from sharinator.administration.views import profile_views

urlpatterns = [
    path('dbadmin/', admin.site.urls),
    path('profile/<int:profile_id>/edit', profile_views.ProfileEditingView.as_view(), name="profileedit"),
    path('profile/edit', profile_views.ProfileRedirectHelperView.as_view(), name="profileeditredirector"),
    path('profile/listprofiles', profile_views.ProfileListView.as_view(), name="profilelist"),
    path('profile/delete', profile_views.DeleteUserView.as_view(), name="deleteuser"),
    path('profile/forceforeignlogout', profile_views.OOBUserLogoutView.as_view(), name="forceforeignlogout"),
    path('profile/add', profile_views.AddUserView.as_view(), name="adduser"),
]
