from django.contrib import admin
from django.urls import path
from main_app import views

urlpatterns = [
    path("dashboard/", views.dashboard, name="dashboard"),
    path("profile/", views.profile_update, name="profile"),
]