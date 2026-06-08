from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from .forms import RegisterForm, LoginForm, EditProfileForm
from .models import User
from django.contrib.auth.decorators import login_required

def register_view(request):

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        if User.objects.filter(username=username).exists():
            return render(request, "users/register.html", {
                "error": "El usuario ya existe"
            })

        user = User.objects.create_user(
            username=username,
            password=password
        )

        login(request, user)

        return redirect("profile", username=user.username)

    return render(request, "users/register.html")

def login_view(request):

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:
            login(request, user)
            return redirect("profile", username=user.username)

        return render(request, "users/login.html", {
            "error": "Credenciales inválidas"
        })

    return render(request, "users/login.html")


def profile_view(request, username):

    profile = get_object_or_404(User, username=username)

    return render(request, "users/profile.html", {
        "profile": profile
    })



@login_required
def edit_profile_view(request):

    user = request.user

    if request.method == "POST":

        user.bio = request.POST.get("bio")
        user.location = request.POST.get("location")
        user.website = request.POST.get("website")

        if "avatar" in request.FILES:
            user.avatar = request.FILES["avatar"]

        user.save()

        return redirect("profile", username=user.username)

    return render(request, "users/edit_profile.html", {
        "user": user
    })


def logout_view(request):
    logout(request)
    return redirect("login")