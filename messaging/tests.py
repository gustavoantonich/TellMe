from django.test import TestCase
from django.urls import reverse
from users.models import User
from .models import Conversation, Message


class MessagingTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username="msguser1", password="pass123")
        self.user2 = User.objects.create_user(username="msguser2", password="pass123")
        self.conversation = Conversation.objects.create()
        self.conversation.participants.add(self.user1, self.user2)
        Message.objects.create(conversation=self.conversation, sender=self.user1, content="Hola!")

    def test_inbox_view(self):
        self.client.login(username="msguser1", password="pass123")
        response = self.client.get(reverse("inbox"))
        self.assertEqual(response.status_code, 200)

    def test_conversation_view(self):
        self.client.login(username="msguser1", password="pass123")
        response = self.client.get(reverse("conversation", args=[self.conversation.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Hola!")

    def test_send_message(self):
        self.client.login(username="msguser1", password="pass123")
        response = self.client.post(reverse("conversation", args=[self.conversation.id]), {
            "content": "Nuevo mensaje"
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Message.objects.filter(content="Nuevo mensaje").exists())

    def test_start_conversation(self):
        self.client.login(username="msguser1", password="pass123")
        response = self.client.get(reverse("start_conversation", args=["msguser2"]))
        self.assertEqual(response.status_code, 302)
