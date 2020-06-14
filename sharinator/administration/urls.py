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
from django.urls import path, re_path

from sharinator.administration.views import profile_views, image_views, management_views

urlpatterns = [
    path('dbadmin/', admin.site.urls),
    path('dashboard', management_views.ManagementDashboardView.as_view(), name="managementdashboard"),
    path('profile/<int:profile_id>/edit', profile_views.ProfileEditingView.as_view(), name="profileedit"),
    path('profile/<int:profile_id>/selectavatar', profile_views.SelectUserAvatarView.as_view(), name="selectavatar"),
    path('profile/edit', profile_views.ProfileRedirectHelperView.as_view(), name="profileeditredirector"),
    path('profile/listprofiles', profile_views.ProfileListView.as_view(), name="profilelist"),
    path('profile/delete', profile_views.DeleteUserView.as_view(), name="deleteuser"),
    path('profile/forceforeignlogout', profile_views.OOBUserLogoutView.as_view(), name="forceforeignlogout"),
    path('profile/add', profile_views.AddUserView.as_view(), name="adduser"),
    path('profile/changepassword', profile_views.ChangePasswordView.as_view(), name="changepassword"),
    path('media/list', image_views.ListMediaView.as_view(), name="listmedia"),
    path('media/<int:image_id>/edit', image_views.EditMediaView.as_view(), name="editmedia"),
    path('media/upload', image_views.SingleMediaUploadView.as_view(), name="uploadsingleimage"),
    path('media/uploadmutliple', image_views.MassMediaUploadView.as_view(), name="uploadmultipleimages"),
    path('media/delete', image_views.DeleteImageView.as_view(), name="deleteimage"),
]
