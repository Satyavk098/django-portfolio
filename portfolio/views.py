from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.core.mail import send_mail
from django.conf import settings
from django.http import JsonResponse

from .models import Project, ContactMessage, Feedback
from .forms import ProjectForm


# =======================
# AUTH (OPTIONAL / LOW VISIBILITY)
# =======================

def register_view(request):
    if request.user.is_authenticated:
        return redirect("home")

    error = None

    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")

        if User.objects.filter(username=username).exists():
            error = "Username already exists"
        else:
            User.objects.create_user(
                username=username,
                email=email,
                password=password,
            )

            # Email should NEVER block registration
            try:
                send_mail(
                    "New User Registered",
                    f"Username: {username}\nEmail: {email}",
                    settings.EMAIL_HOST_USER,
                    [settings.EMAIL_HOST_USER],
                )

                send_mail(
                    "Welcome!",
                    f"Hi {username}, thanks for registering!",
                    settings.EMAIL_HOST_USER,
                    [email],
                )
            except Exception as e:
                print("Email failed:", e)

            return redirect("login")

    return render(request, "portfolio/register.html", {"error": error})


def login_view(request):
    if request.user.is_authenticated:
        return redirect("home")

    error = None

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return redirect("home")
        else:
            error = "Invalid username or password"

    return render(request, "portfolio/login.html", {"error": error})


def logout_view(request):
    logout(request)
    return redirect("home")


# =======================
# PUBLIC PAGES (PORTFOLIO)
# =======================

def home(request):
    projects = Project.objects.all()[:3]
    return render(request, "portfolio/home.html", {"projects": projects})


def projects(request):
    projects = Project.objects.all().order_by("-created_at")
    return render(request, "portfolio/projects.html", {"projects": projects})


def project_detail(request, slug):
    project = get_object_or_404(Project, slug=slug)
    return render(request, "portfolio/project_detail.html", {"project": project})


def contact(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        message = request.POST.get("message")

        ContactMessage.objects.create(
            name=name,
            email=email,
            message=message,
        )

        try:
            send_mail(
                "New Portfolio Contact Message",
                message,
                email,
                [settings.EMAIL_HOST_USER],
            )
        except Exception as e:
            print("Email failed:", e)

        return redirect("home")

    return render(request, "portfolio/contact.html")


def feedback(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        message = request.POST.get("message")

        Feedback.objects.create(
            name=name,
            email=email,
            message=message,
        )

        try:
            send_mail(
                "New Portfolio Feedback",
                message,
                email,
                [settings.EMAIL_HOST_USER],
            )
        except Exception as e:
            print("Email failed:", e)

        return redirect("home")

    return render(request, "portfolio/feedback.html")


# =======================
# DASHBOARD (STAFF ONLY)
# =======================

@staff_member_required
def dashboard(request):
    projects = Project.objects.all().order_by("-created_at")
    return render(request, "portfolio/dashboard.html", {"projects": projects})


@staff_member_required
def project_add(request):
    if request.method == "POST":
        form = ProjectForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("dashboard")
    else:
        form = ProjectForm()

    return render(request, "portfolio/project_form.html", {"form": form})


@staff_member_required
def project_edit(request, pk):
    project = get_object_or_404(Project, pk=pk)

    if request.method == "POST":
        form = ProjectForm(request.POST, request.FILES, instance=project)
        if form.is_valid():
            form.save()
            return redirect("dashboard")
    else:
        form = ProjectForm(instance=project)

    return render(request, "portfolio/project_form.html", {"form": form})


@staff_member_required
def project_delete(request, pk):
    project = get_object_or_404(Project, pk=pk)

    if request.method == "POST":
        project.delete()
        return redirect("dashboard")

    return render(
        request,
        "portfolio/project_confirm_delete.html",
        {"project": project},
    )


# =======================
# API (PUBLIC, READ-ONLY)
# =======================

def projects_api(request):
    projects = Project.objects.all().order_by("-created_at")

    data = [
        {
            "id": p.id,
            "title": p.title,
            "slug": p.slug,
            "description": p.description,
            "created_at": p.created_at.isoformat(),
        }
        for p in projects
    ]

    return JsonResponse(data, safe=False)