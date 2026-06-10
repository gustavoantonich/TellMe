import re

from django.db import models
from django.conf import settings
from django.utils.text import slugify


class Hashtag(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return f"#{self.name}"


class Post(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
on_delete=models.CASCADE, related_name="posts")
    content = models.TextField()
    image = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    hashtags = models.ManyToManyField(Hashtag, related_name="posts", blank=True)

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new or kwargs.get("update_hashtags", True):
            self._update_hashtags()

    def _update_hashtags(self):
        names = set(re.findall(r'#(\w+)', self.content))
        tags = []
        for name in names:
            tag, _ = Hashtag.objects.get_or_create(name=name.lower())
            tags.append(tag)
        self.hashtags.set(tags)

    def __str__(self):
        return f"{self.user.username}: {self.content[:30]}"


class Like(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("user", "post")