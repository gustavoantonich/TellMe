from django.urls import path
from . import views

urlpatterns = [
    path("", views.feed, name="feed"),
    path("like/<int:post_id>/", views.like_post, name="like_post"),
    path("retweet/<int:post_id>/", views.retweet_post, name="retweet_post"),
    path("reply/<int:post_id>/", views.reply_view, name="reply"),
    path("thread/<int:post_id>/", views.thread_view, name="thread"),
    path("delete/<int:post_id>/", views.delete_post, name="delete_post"),
    path("hashtag/<slug:tag_name>/", views.hashtag_view, name="hashtag"),
]
