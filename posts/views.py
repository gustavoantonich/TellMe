from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.db.models import Count
from .models import Post, Like, Hashtag
from .forms import PostForm


def feed(request):
    posts = Post.objects.select_related('user').annotate(
        likes_count=Count('like')
    ).order_by('-created_at')

    liked_post_ids = []
    if request.user.is_authenticated:
        liked_post_ids = list(Like.objects.filter(
            user=request.user,
            post_id__in=[p.id for p in posts]
        ).values_list('post_id', flat=True))

    if request.method == "POST" and request.user.is_authenticated:
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            return redirect('feed')
    else:
        form = PostForm()

    trending = Hashtag.objects.annotate(
        post_count=Count('posts')
    ).filter(post_count__gt=0).order_by('-post_count')[:5]

    return render(request, "posts/feed.html", {
        "posts": posts,
        "form": form,
        "liked_post_ids": liked_post_ids,
        "trending": trending,
    })


def hashtag_view(request, tag_name):
    hashtag = get_object_or_404(
        Hashtag,
        name=tag_name.lower()
    )

    posts = hashtag.posts.select_related('user').annotate(
        likes_count=Count('like')
    ).order_by('-created_at')

    liked_post_ids = []

    if request.user.is_authenticated:
        liked_post_ids = list(
            Like.objects.filter(
                user=request.user,
                post_id__in=[p.id for p in posts]
            ).values_list('post_id', flat=True)
        )

    # NUEVO: permitir publicar desde la página del hashtag
    if request.method == "POST" and request.user.is_authenticated:
        form = PostForm(request.POST)

        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user

            content = post.content.strip()

            if not content.lower().startswith(f"#{hashtag.name}"):
                post.content = f"#{hashtag.name} {content}"

            post.save()

            return redirect(
                "hashtag",
                tag_name=hashtag.name
            )

    else:
        form = PostForm()

    return render(
        request,
        "posts/feed.html",
        {
            "posts": posts,
            "hashtag": hashtag,
            "liked_post_ids": liked_post_ids,
            "form": form,
        }
    )


@login_required
@require_POST
def like_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    like, created = Like.objects.get_or_create(
        user=request.user,
        post=post
    )
    if not created:
        like.delete()
        liked = False
    else:
        liked = True

    return JsonResponse({
        'liked': liked,
        'likes_count': post.like_set.count(),
    })
