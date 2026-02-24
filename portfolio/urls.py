from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),

    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.register_view, name="register"),

    path("api/projects/", views.projects_api, name="projects_api"),
    
    path("projects/", views.projects, name="projects"),
    path("projects/<slug:slug>/", views.project_detail, name="project_detail"),

    path("feedback/", views.feedback, name="feedback"),
    path("contact/", views.contact, name="contact"),

    path("dashboard/", views.dashboard, name="dashboard"),
    path("dashboard/add/", views.project_add, name="project_add"),
    path("dashboard/edit/<int:pk>/", views.project_edit, name="project_edit"),
    path("dashboard/delete/<int:pk>/", views.project_delete, name="project_delete"),
]