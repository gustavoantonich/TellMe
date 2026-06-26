from django.urls import path
from . import views

urlpatterns = [
    path("", views.inbox_view, name="inbox"),
    path("<int:conversation_id>/", views.conversation_view, name="conversation"),
    path("new/<str:username>/", views.start_conversation_view, name="start_conversation"),
]
