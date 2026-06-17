import re
import uuid

from django.db import models
from django.conf import settings


class Hashtag(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return f"#{self.name}"


class Post(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="posts")
    content = models.TextField(max_length=500)
    image = models.ImageField(upload_to="posts/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    hashtags = models.ManyToManyField(Hashtag, related_name="posts", blank=True)

    parent = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.CASCADE,
        related_name="replies"
    )
    thread_id = models.UUIDField(null=True, blank=True, db_index=True)

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        if is_new and self.parent_id and not self.thread_id:
            if self.parent.thread_id:
                self.thread_id = self.parent.thread_id
            else:
                self.thread_id = self.parent.pk
        super().save(*args, **kwargs)
        if is_new or kwargs.get("update_hashtags", True):
            self._update_hashtags()

    def _update_hashtags(self):
        names = set(re.findall(r"#(\w+)", self.content))
        tags = [Hashtag.objects.get_or_create(name=n.lower())[0] for n in names]
        self.hashtags.set(tags)

    def is_reply(self):
        return self.parent_id is not None

    def __str__(self):
        return f"{self.user.username}: {self.content[:30]}"


class Like(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("user", "post")


class Retweet(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="retweets")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "post")

    def __str__(self):
        return f"{self.user.username} retweeted {self.post.user.username}"