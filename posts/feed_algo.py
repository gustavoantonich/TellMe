import math
from django.utils import timezone
from django.core.cache import cache


def compute_post_score(post, now=None, following_ids=None):
    if now is None:
        now = timezone.now()

    hours_ago = (now - post.created_at).total_seconds() / 3600

    likes = getattr(post, 'likes_count', 0) or 0
    retweets = getattr(post, 'retweets_count', 0) or 0
    replies = getattr(post, 'replies_count', 0) or 0

    engagement = likes + 2 * retweets + 3 * replies
    recency = 1.0 / (1.0 + math.sqrt(hours_ago))
    score = (1.0 + engagement) * recency * 100.0

    if following_ids and post.user_id in following_ids:
        score *= 3.0

    return round(score, 1)


def score_and_sort_posts(posts, user=None, following_ids=None):
    now = timezone.now()
    scored = []
    for post in posts:
        post.algorithmic_score = compute_post_score(post, now, following_ids)
        scored.append(post)
    scored.sort(key=lambda p: p.algorithmic_score, reverse=True)
    return scored


def get_cached_feed(tab, user_id, timeout=120):
    cache_key = f"feed_{tab}_v1"
    if tab == "following" and user_id:
        cache_key = f"feed_following_{user_id}_v1"
    return cache.get(cache_key)


def set_cached_feed(tab, user_id, posts, timeout=120):
    cache_key = f"feed_{tab}_v1"
    if tab == "following" and user_id:
        cache_key = f"feed_following_{user_id}_v1"
    cache.set(cache_key, posts, timeout)


def invalidate_feed_cache():
    keys = [
        "feed_global_v1",
        "trending_hashtags_v1",
    ]
    cache.delete_many(keys)


def invalidate_feed_for_user(user_id):
    cache.delete(f"feed_following_{user_id}_v1")
    cache.delete("feed_global_v1")
