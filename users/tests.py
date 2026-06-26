from django.test import TestCase
from django.urls import reverse
from .models import User


class UserTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="pass123", email="test@test.com")

    def test_register_view_get(self):
        response = self.client.get(reverse("register"))
        self.assertEqual(response.status_code, 200)

    def test_register_view_post(self):
        response = self.client.post(reverse("register"), {
            "username": "newuser",
            "email": "new@test.com",
            "password1": "complexpass123",
            "password2": "complexpass123",
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username="newuser").exists())

    def test_login_view(self):
        response = self.client.post(reverse("login"), {
            "username": "testuser",
            "password": "pass123",
        })
        self.assertEqual(response.status_code, 302)

    def test_profile_view(self):
        response = self.client.get(reverse("profile", args=["testuser"]))
        self.assertEqual(response.status_code, 200)

    def test_user_search_autocomplete(self):
        response = self.client.get(reverse("user_search") + "?q=test")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "testuser")
