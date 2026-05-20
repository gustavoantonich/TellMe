from django.contrib import admin
from .models import Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('author', 'content', 'created_at')
    search_fields = ('content', 'author__username')
    list_filter = ('created_at',)
    
# Añadido 4 sas sas