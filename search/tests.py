from django.test import TestCase
from django.urls import reverse
from users.models import User


class SearchTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="searchable", password="pass123", email="search@test.com")

    def test_search_view_get(self):
        response = self.client.get(reverse("search"))
        self.assertEqual(response.status_code, 200)

    def test_search_with_query(self):
        response = self.client.get(reverse("search") + "?q=search")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "searchable")
