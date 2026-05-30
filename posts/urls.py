from django.urls import path
from .views import feed, create_post

urlpatterns = [
    path('', feed, name='feed'),
    path('create/', create_post, name='create_post'),
]
#añadido 6 c4