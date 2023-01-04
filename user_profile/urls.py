from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from user_profile.views import login_user
from django.views.generic.base import RedirectView
from django.urls import include, path, re_path
from .views import *

urlpatterns = [
    path('redirect-admin', RedirectView.as_view(url="/admin"), name="redirect-admin"),
    path('login/', login_user, name='login'),
    
    path('logout/', logout_user, name='logout'),
    path('register_user/', register_user, name='register_user'),
    path('profile/', profile, name='profile'),
    path('change_profile_picture/', change_profile_picture,
         name='change_profile_picture'),
    path('view_user_information/<str:username>/',
         view_user_information, name="view_user_information"),
    path('follow_or_unfollow/<int:user_id>/',
         follow_or_unfollow_user, name='follow_or_unfollow_user'),
    path('user_notifications/', user_notifications, name='user_notifications'),
    path('mute_or_unmute_user/<int:user_id>/',
         mute_or_unmute_user, name='mute_or_unmute_user'),
    path('password_change/', auth_views.PasswordChangeView.as_view(
         template_name='registration/password_change.html', success_url='/'), name='password_change'),
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(template_name='registration/password_change_done.html'),
         name='password_change_done'),
    path('password_reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_done.html'),
         name='password_reset_done'),

    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(),
         name='password_reset_confirm'),

    path('password_reset/', auth_views.PasswordResetView.as_view(),
         name='password_reset'),

    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'),
         name='password_reset_complete'),
]
