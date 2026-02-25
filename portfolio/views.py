from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
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
            User.objects.create_user(
                username=username,
                email=email,
                password=password,
                is_staff=True
            )
            return redirect("login")

    return render(request, "register.html", {"error": error})


def login_view(request):
    if request.user.is_authenticated:
        return redirect("home")

    error = None

    if request.method == "POST":
        user = authenticate(
            request,
            username=request.POST.get("username"),
            password=request.POST.get("password"),
        )

        if user:
            login(request, user)
            next_url = request.GET.get("next")
            return redirect(next_url or "dashboard")
        else:
            error = "Invalid username or password"

    return render(request, "login.html", {"error": error})


def logout_view(request):
    logout(request)
    return redirect("home")


# =======================
# PUBLIC PAGES
# =======================

def home(request):
    projects = Project.objects.all()[:3]
    return render(request, "home.html", {"projects": projects})


def projects(request):
    projects = Project.objects.all().order_by("-created_at")
    return render(request, "projects.html", {"projects": projects})


def project_detail(request, slug):
    project = get_object_or_404(Project, slug=slug)
    return render(request, "project_detail.html", {"project": project})


def contact(request):
    if request.method == "POST":
        ContactMessage.objects.create(
            name=request.POST.get("name"),
            email=request.POST.get("email"),
            message=request.POST.get("message"),
        )
        return redirect("home")

    return render(request, "contact.html")


def feedback(request):
    if request.method == "POST":
        Feedback.objects.create(
            name=request.POST.get("name"),
            email=request.POST.get("email"),
            message=request.POST.get("message"),
        )
        return redirect("home")

    return render(request, "feedback.html")


# =======================
# DASHBOARD (LOGIN + STAFF REQUIRED)
# =======================

@login_required(login_url="login")
@staff_member_required
def dashboard(request):
    projects = Project.objects.all().order_by("-created_at")
    return render(request, "dashboard.html", {"projects": projects})


@login_required(login_url="login")
@staff_member_required
def project_add(request):
    form = ProjectForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        form.save()
        return redirect("dashboard")

    return render(request, "project_form.html", {"form": form})


@login_required(login_url="login")
@staff_member_required
def project_edit(request, pk):
    project = get_object_or_404(Project, pk=pk)
    form = ProjectForm(request.POST or None, request.FILES or None, instance=project)

    if form.is_valid():
        form.save()
        return redirect("dashboard")

    return render(request, "project_form.html", {"form": form})


@login_required(login_url="login")
@staff_member_required
def project_delete(request, pk):
    project = get_object_or_404(Project, pk=pk)

    if request.method == "POST":
        project.delete()
        return redirect("dashboard")

    return render(request, "project_confirm_delete.html", {"project": project})


