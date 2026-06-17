from django.contrib import admin
from .models import Post, Hashtag, Like, Retweet


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('user', 'content', 'created_at', 'is_reply')
    search_fields = ('content', 'user__username')
    list_filter = ('created_at',)
    filter_horizontal = ('hashtags',)

    def is_reply(self, obj):
        return obj.parent_id is not None
    is_reply.boolean = True
    is_reply.short_description = "Reply"


@admin.register(Hashtag)
class HashtagAdmin(admin.ModelAdmin):
    list_display = ('name', 'post_count')
    search_fields = ('name',)

    def post_count(self, obj):
        return obj.posts.count()
    post_count.short_description = 'Posts'


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'post_created_at')
    search_fields = ('user__username',)

    def post_created_at(self, obj):
        return obj.post.created_at
    post_created_at.short_description = 'Fecha del post'


@admin.register(Retweet)
class RetweetAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'created_at')
    search_fields = ('user__username', 'post__content')