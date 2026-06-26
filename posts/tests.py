from django.test import TestCase
from django.urls import reverse
from .models import Post, Hashtag, Like
from users.models import User


class PostTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="postuser", password="pass123")

    def test_feed_view(self):
        response = self.client.get(reverse("feed"))
        self.assertEqual(response.status_code, 200)

    def test_create_post(self):
        self.client.login(username="postuser", password="pass123")
        response = self.client.post(reverse("feed"), {"content": "Test post #test"})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Post.objects.filter(content="Test post #test").exists())

    def test_hashtag_created_on_post(self):
        self.client.login(username="postuser", password="pass123")
        self.client.post(reverse("feed"), {"content": "Post with #python"})
        self.assertTrue(Hashtag.objects.filter(name="python").exists())

    def test_like_post(self):
        post = Post.objects.create(user=self.user, content="Likeable post")
        self.client.login(username="postuser", password="pass123")
        response = self.client.post(reverse("like_post", args=[post.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Like.objects.filter(user=self.user, post=post).exists())

    def test_hashtag_view(self):
        hashtag = Hashtag.objects.create(name="django")
        Post.objects.create(user=self.user, content="Django post")
        hashtag.posts.add(Post.objects.first())
        response = self.client.get(reverse("hashtag", args=["django"]))
        self.assertEqual(response.status_code, 200)
