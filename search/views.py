from django.shortcuts import render
from django.db.models import Count, Q
from posts.models import Post, Hashtag, Like
from users.models import User


def search_view(request):
    q = request.GET.get("q", "").strip()

    posts = Post.objects.none()
    users = User.objects.none()
    hashtags = Hashtag.objects.none()

    if q:
        posts = (
            Post.objects.filter(
                Q(content__icontains=q) | Q(user__username__icontains=q)
            )
            .filter(parent=None)
            .select_related("user")
            .prefetch_related("hashtags")
            .annotate(
                likes_count=Count("like", distinct=True),
                retweets_count=Count("retweets", distinct=True),
                replies_count=Count("replies", distinct=True),
            )
            .order_by("-created_at")[:20]
        )
        users = User.objects.filter(
            Q(username__icontains=q) | Q(bio__icontains=q) | Q(email__icontains=q)
        ).annotate(
            followers_count=Count("followers", distinct=True),
            posts_count=Count("posts", distinct=True),
        )[:10]
        hashtags = (
            Hashtag.objects.filter(name__icontains=q)
            .annotate(post_count=Count("posts"))
            .order_by("-post_count")[:5]
        )

    liked_post_ids = []
    if request.user.is_authenticated:
        liked_post_ids = list(
            Like.objects.filter(
                user=request.user,
                post_id__in=[p.id for p in posts],
            ).values_list("post_id", flat=True)
        )

    return render(request, "search/search.html", {
        "query": q,
        "posts": posts,
        "users": users,
        "hashtags": hashtags,
        "liked_post_ids": liked_post_ids,
    })
