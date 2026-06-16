from django.urls import path
from . import views

urlpatterns = [
    path("", views.feed, name="feed"),
    path("like/<int:post_id>/", views.like_post, name="like_post"),
    path("delete/<int:post_id>/", views.delete_post, name="delete_post"),
    path("hashtag/<slug:tag_name>/", views.hashtag_view, name="hashtag"),
]
