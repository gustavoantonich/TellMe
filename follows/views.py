from django.shortcuts import render, redirect, get_object_or_404
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

    next_url = request.POST.get("next", "")
    if next_url:
        return redirect(next_url)
    return redirect("profile", username=username)


def followers_list(request, username):
    profile = get_object_or_404(User, username=username)
    followers = User.objects.filter(following__following=profile)
    is_following_map = _get_following_map(request, followers)
    return render(request, "follows/user_list.html", {
        "title": f"Seguidores de @{profile.username}",
        "profile": profile,
        "users": followers,
        "is_following_map": is_following_map,
    })


def following_list(request, username):
    profile = get_object_or_404(User, username=username)
    following = User.objects.filter(followers__follower=profile)
    is_following_map = _get_following_map(request, following)
    return render(request, "follows/user_list.html", {
        "title": f"Siguiendo de @{profile.username}",
        "profile": profile,
        "users": following,
        "is_following_map": is_following_map,
    })


def _get_following_map(request, users):
    if not request.user.is_authenticated:
        return {}
    user_ids = [u.id for u in users]
    following_ids = set(
        Follow.objects.filter(
            follower=request.user, following_id__in=user_ids
        ).values_list("following_id", flat=True)
    )
    return {uid: True for uid in following_ids}
