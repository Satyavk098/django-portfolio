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
# AUTH
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
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
            )

            # EMAIL TO ADMIN
            send_mail(
                subject="New User Registered",
                message=f"New user registered:\n\nUsername: {username}\nEmail: {email}",
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[settings.EMAIL_HOST_USER],
                fail_silently=False,
            )

            # EMAIL TO USER
            send_mail(
                subject="Welcome to My Portfolio",
                message=f"Hi {username},\n\nThanks for registering on my portfolio!",
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[email],
                fail_silently=False,
            )

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
            next_url = request.GET.get("next")
            return redirect(next_url or "home")
        else:
            error = "Invalid username or password"

    return render(request, "portfolio/login.html", {"error": error})


@login_required
def logout_view(request):
    logout(request)
    return redirect("login")


# =======================
# HOME / PROJECTS
# =======================

@login_required
def home(request):
    projects = Project.objects.all()[:3]
    return render(request, "portfolio/home.html", {"projects": projects})


@login_required
def projects(request):
    projects = Project.objects.all().order_by("-created_at")
    return render(request, "portfolio/projects.html", {"projects": projects})


@login_required
def project_detail(request, slug):
    project = get_object_or_404(Project, slug=slug)
    return render(request, "portfolio/project_detail.html", {"project": project})


# =======================
# FEEDBACK / CONTACT
# =======================

@login_required
def feedback(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        message = request.POST.get("message")

        Feedback.objects.create(name=name, email=email, message=message)

        send_mail(
            "New Portfolio Feedback",
            message,
            email,
            [settings.EMAIL_HOST_USER],
            fail_silently=False,
        )

        return redirect("home")

    return render(request, "portfolio/feedback.html")


def contact(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        message = request.POST.get("message")

        ContactMessage.objects.create(name=name, email=email, message=message)

        send_mail(
            "New Portfolio Contact Message",
            message,
            email,
            [settings.EMAIL_HOST_USER],
            fail_silently=False,
        )

        return redirect("home")

    return render(request, "portfolio/contact.html")


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

    return render(request, "portfolio/project_confirm_delete.html", {"project": project})


# =======================
# API
# =======================

def projects_api(request):
    projects = Project.objects.all().order_by("-created_at")

    data = [
        {
            "id": p.id,
            "title": p.title,
            "slug": p.slug,
            "description": p.description,
            "created_at": p.created_at,
        }
        for p in projects
    ]

    return JsonResponse(data, safe=False)