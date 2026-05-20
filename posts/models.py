from django.db import models
from django.conf import settings


class Post(models.Model):
    """
    Modelo principal de publicaciones en TellMe.
    """

    # Usuario autor del post
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='posts'
    )

    # Contenido del post
    content = models.TextField(max_length=280)

    # Imagen opcional
    image = models.ImageField(
        upload_to='posts/',
        blank=True,
        null=True
    )

    # Fecha de creación automática
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.author.username}: {self.content[:25]}"
    
    # Añadido 3 sus