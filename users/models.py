from django.db import models
from django.contrib.auth.models import AbstractUser

# Modelo personalizado de usuario
class User(AbstractUser):

    # Biografía del usuario
    bio = models.TextField(
        max_length=300,
        blank=True
    )

    # Imagen de perfil
    avatar = models.ImageField(

        # Carpeta donde se guardarán
        upload_to='avatars/',

        blank=True,
        null=True
    )

    # Fecha de creación de cuenta
    created_at = models.DateTimeField(
        auto_now_add=True
    )

    # Cómo aparecerá el usuario
    def __str__(self):
        return self.username
    
    #añadido 2 ñoño