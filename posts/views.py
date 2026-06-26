from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.db.models import Count
from .models import Post, Like, Hashtag, Retweet
from .forms import PostForm
from .feed_algo import score_and_sort_posts, get_cached_feed, set_cached_feed, invalidate_feed_cache, invalidate_feed_for_user
from follows.models import Follow


def feed(request):
    tab = request.GET.get("tab", "global")

    following_ids = set()
    if request.user.is_authenticated:
        following_ids = set(
            Follow.objects.filter(follower=request.user).values_list("following_id", flat=True)
        )

    cached = get_cached_feed(tab, request.user.pk if request.user.is_authenticated else None)
    if cached is not None:
        post_ids, liked_post_ids, retweeted_post_ids = cached
        base_posts = Post.objects.filter(id__in=post_ids).select_related("user").prefetch_related("hashtags").annotate(
            likes_count=Count("like", distinct=True),
            retweets_count=Count("retweets", distinct=True),
            replies_count=Count("replies", distinct=True),
        )
        post_order = {pid: i for i, pid in enumerate(post_ids)}
        base_posts = sorted(base_posts, key=lambda p: post_order.get(p.id, 0))
    else:
        base_qs = Post.objects.filter(parent=None).select_related("user").prefetch_related("hashtags")

        if request.user.is_authenticated and tab == "following":
            base_qs = base_qs.filter(user_id__in=following_ids)

        base_posts = list(base_qs.annotate(
            likes_count=Count("like", distinct=True),
            retweets_count=Count("retweets", distinct=True),
            replies_count=Count("replies", distinct=True),
        ))

        liked_post_ids = []
        retweeted_post_ids = set()
        if request.user.is_authenticated:
            liked_post_ids = list(
                Like.objects.filter(
                    user=request.user,
                    post_id__in=[p.id for p in base_posts],
                ).values_list("post_id", flat=True)
            )
            retweeted_post_ids = set(
                Retweet.objects.filter(
                    user=request.user,
                    post_id__in=[p.id for p in base_posts],
                ).values_list("post_id", flat=True)
            )

        base_posts = score_and_sort_posts(base_posts, request.user, following_ids)
        post_ids = [p.id for p in base_posts]
        set_cached_feed(tab, request.user.pk if request.user.is_authenticated else None,
                        (post_ids, liked_post_ids, retweeted_post_ids))

    parent_id = request.GET.get("reply_to")
    initial = {}
    if parent_id:
        parent = get_object_or_404(Post, id=parent_id)
        initial = {"parent": parent}

    if request.method == "POST" and request.user.is_authenticated:
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.parent_id = request.POST.get("parent_id") or None
            post.save()
            invalidate_feed_cache()
            if request.user.is_authenticated:
                invalidate_feed_for_user(request.user.pk)
            return redirect("feed")
    else:
        form = PostForm(initial=initial)

    trending = Hashtag.objects.annotate(
        post_count=Count("posts")
    ).filter(post_count__gt=0).order_by("-post_count")[:5]

    reply_to = None
    if parent_id:
        reply_to = get_object_or_404(Post.objects.select_related("user"), id=parent_id)

    return render(request, "posts/feed.html", {
        "posts": base_posts,
        "form": form,
        "liked_post_ids": liked_post_ids if cached is None else cached[1],
        "retweeted_post_ids": retweeted_post_ids if cached is None else cached[2],
        "following_ids": following_ids,
        "trending": trending,
        "reply_to": reply_to,
        "tab": tab,
    })


def hashtag_view(request, tag_name):
    hashtag = get_object_or_404(
        Hashtag,
        name=tag_name.lower()
    )

    posts = hashtag.posts.select_related('user').prefetch_related('hashtags').annotate(
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

    if request.method == "POST" and request.user.is_authenticated:
        form = PostForm(request.POST, request.FILES)

        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user

            content = post.content.strip()

            if f"#{hashtag.name.lower()}" not in content.lower():
                post.content = f"{content} #{hashtag.name}"

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

    invalidate_feed_cache()

    return JsonResponse({
        "liked": liked,
        "likes_count": post.like_set.count(),
    })


@login_required
@require_POST
def retweet_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    retweet, created = Retweet.objects.get_or_create(
        user=request.user,
        post=post,
    )
    if not created:
        retweet.delete()
        retweeted = False
    else:
        retweeted = True

    invalidate_feed_cache()

    return JsonResponse({
        "retweeted": retweeted,
        "retweets_count": post.retweets.count(),
    })


@login_required
def reply_view(request, post_id):
    parent = get_object_or_404(
        Post.objects.select_related("user"), id=post_id
    )
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.parent = parent
            post.save()
            return redirect("feed")
    else:
        form = PostForm(initial={"parent": parent})

    return render(request, "posts/reply.html", {
        "form": form,
        "parent": parent,
    })


def thread_view(request, post_id):
    post = get_object_or_404(
        Post.objects.select_related("user").prefetch_related("hashtags").annotate(
            likes_count=Count("like", distinct=True),
            retweets_count=Count("retweets", distinct=True),
            replies_count=Count("replies", distinct=True),
        ),
        id=post_id,
    )
    replies = Post.objects.filter(parent=post).select_related("user").prefetch_related("hashtags").annotate(
        likes_count=Count("like", distinct=True),
        retweets_count=Count("retweets", distinct=True),
        replies_count=Count("replies", distinct=True),
    ).order_by("created_at")

    liked_post_ids = []
    retweeted_post_ids = set()
    if request.user.is_authenticated:
        all_ids = [post.id] + [r.id for r in replies]
        liked_post_ids = list(
            Like.objects.filter(user=request.user, post_id__in=all_ids)
            .values_list("post_id", flat=True)
        )
        retweeted_post_ids = set(
            Retweet.objects.filter(user=request.user, post_id__in=all_ids)
            .values_list("post_id", flat=True)
        )

    return render(request, "posts/thread.html", {
        "post": post,
        "replies": replies,
        "liked_post_ids": liked_post_ids,
        "retweeted_post_ids": retweeted_post_ids,
    })


@login_required
@require_POST
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id, user=request.user)
    post.delete()
    return redirect("feed")
