from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from .forms import EditProfileForm
from .models import User
from posts.models import Post


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

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("profile", username=user.username)

        return render(request, "users/login.html", {
            "error": "Credenciales invalidas"
        })

    return render(request, "users/login.html")


def profile_view(request, username):
    profile = get_object_or_404(User, username=username)

    posts = Post.objects.filter(user=profile).annotate(
        likes_count=Count('like')
    ).order_by('-created_at')

    posts_count = posts.count()
    followers_count = profile.followers.count()
    following_count = profile.following.count()

    return render(request, "users/profile.html", {
        "profile": profile,
        "posts": posts,
        "posts_count": posts_count,
        "followers_count": followers_count,
        "following_count": following_count,
    })


@login_required
def edit_profile_view(request):
    user = request.user

    if request.method == "POST":
        form = EditProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect("profile", username=user.username)
    else:
        form = EditProfileForm(instance=user)

    return render(request, "users/edit_profile.html", {
        "form": form,
    })


def logout_view(request):
    logout(request)
    return redirect("login")
