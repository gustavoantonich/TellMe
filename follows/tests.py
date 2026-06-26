from django.test import TestCase
from django.urls import reverse
from users.models import User


class FollowTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username="user1", password="pass123")
        self.user2 = User.objects.create_user(username="user2", password="pass123")

    def test_follow_user(self):
        self.client.login(username="user1", password="pass123")
        response = self.client.post(reverse("toggle_follow", args=["user2"]), {"next": "/"})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(self.user1.following.filter(following=self.user2).exists())

    def test_unfollow_user(self):
        self.client.login(username="user1", password="pass123")
        self.client.post(reverse("toggle_follow", args=["user2"]))
        response = self.client.post(reverse("toggle_follow", args=["user2"]))
        self.assertFalse(self.user1.following.filter(following=self.user2).exists())

    def test_followers_list(self):
        response = self.client.get(reverse("followers_list", args=["user1"]))
        self.assertEqual(response.status_code, 200)

    def test_following_list(self):
        response = self.client.get(reverse("following_list", args=["user1"]))
        self.assertEqual(response.status_code, 200)
