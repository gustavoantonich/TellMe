from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from .forms import RegisterForm, LoginForm, EditProfileForm
from .models import User
from posts.models import Post


def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("profile", username=user.username)
    else:
        form = RegisterForm()

    return render(request, "users/register.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("profile", username=user.username)
    else:
        form = LoginForm()

    return render(request, "users/login.html", {"form": form})


def profile_view(request, username):
    profile = get_object_or_404(User, username=username)

    posts = Post.objects.filter(user=profile).annotate(
        likes_count=Count('like')
    ).order_by('-created_at')

    posts_count = posts.count()
    followers_count = profile.followers.count()
    following_count = profile.following.count()

    is_following = False
    if request.user.is_authenticated and request.user != profile:
        is_following = profile.followers.filter(follower=request.user).exists()

    return render(request, "users/profile.html", {
        "profile": profile,
        "posts": posts,
        "posts_count": posts_count,
        "followers_count": followers_count,
        "following_count": following_count,
        "is_following": is_following,
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
