from django.urls import path

from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("students/", views.students, name="students"),
    path("courses/", views.courses, name="courses"),
    path("lecturers/", views.lecturers, name="lecturers"),
    path("departments/", views.departments, name="departments"),
    path("profile/", views.profile, name="profile"),
    path("settings/", views.settings, name="settings"),
]
