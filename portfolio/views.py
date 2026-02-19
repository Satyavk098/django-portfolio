from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.core.mail import send_mail
from django.conf import settings

from .models import Project, ContactMessage, Feedback
from .forms import ProjectForm


# ---------------- AUTH ----------------

def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']

        User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
        return redirect('login')

    return render(request, 'portfolio/register.html')


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    error = None

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            next_url = request.GET.get('next')
            return redirect(next_url if next_url else 'home')
        else:
            error = "Invalid username or password"

    return render(request, 'portfolio/login.html', {'error': error})


def logout_view(request):
    logout(request)
    return redirect('login')


# ---------------- HOME ----------------

@login_required
def home(request):
    projects = Project.objects.all()[:3]
    return render(
        request,
        'portfolio/home.html',
        {
            'projects': projects,
            'MEDIA_URL': settings.MEDIA_URL
        }
    )


# ---------------- FEEDBACK / CONTACT ----------------

@login_required
def feedback(request):
    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']
        message = request.POST['message']

        Feedback.objects.create(
            name=name,
            email=email,
            message=message
        )

        send_mail(
            'New Portfolio Feedback',
            message,
            email,
            [settings.EMAIL_HOST_USER],
        )

        send_mail(
            'Thank You for Your Feedback',
            'Thanks for your feedback! I really appreciate it.',
            settings.EMAIL_HOST_USER,
            [email],
        )

        return redirect('home')

    return render(request, 'portfolio/feedback.html')


def contact(request):
    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']
        message = request.POST['message']

        ContactMessage.objects.create(
            name=name,
            email=email,
            message=message
        )

        send_mail(
            'New Portfolio Contact Message',
            message,
            email,
            [settings.EMAIL_HOST_USER],
        )

        send_mail(
            'Thanks for contacting me',
            'Thank you for reaching out. I will get back to you soon.',
            settings.EMAIL_HOST_USER,
            [email],
        )

        return redirect('home')

    return render(request, 'portfolio/contact.html')


# ---------------- PROJECTS ----------------

@login_required
def projects(request):
    projects = Project.objects.all().order_by('-created_at')
    return render(request, 'portfolio/projects.html', {'projects': projects})


@login_required
def project_detail(request, slug):
    project = get_object_or_404(Project, slug=slug)
    return render(request, 'portfolio/project_detail.html', {'project': project})


# ---------------- DASHBOARD (ADMIN ONLY) ----------------

@staff_member_required
def dashboard(request):
    projects = Project.objects.all().order_by('-created_at')
    return render(request, 'portfolio/dashboard.html', {'projects': projects})


@staff_member_required
def project_add(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = ProjectForm()

    return render(request, 'portfolio/project_form.html', {'form': form})


@staff_member_required
def project_edit(request, pk):
    project = get_object_or_404(Project, pk=pk)

    if request.method == 'POST':
        form = ProjectForm(request.POST, request.FILES, instance=project)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = ProjectForm(instance=project)

    return render(request, 'portfolio/project_form.html', {'form': form})


@staff_member_required
def project_delete(request, pk):
    project = get_object_or_404(Project, pk=pk)

    if request.method == 'POST':
        project.delete()
        return redirect('dashboard')

    return render(request, 'portfolio/project_confirm_delete.html', {'project': project})
