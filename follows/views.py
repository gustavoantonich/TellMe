from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from .models import Follow

User = get_user_model()


@login_required
def toggle_follow(request, username):
    target = get_object_or_404(User, username=username)

    if request.user == target:
        return redirect('profile', username=username)

    follow, created = Follow.objects.get_or_create(
        follower=request.user,
        following=target
    )

    if not created:
        follow.delete()

    return redirect('profile', username=username)
