from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from posts.models import Post, Like
from datetime import timedelta
from django.utils import timezone
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Crea datos de ejemplo para la red social'

    def handle(self, *args, **options):
        if User.objects.count() > 2:
            self.stdout.write(self.style.WARNING('Ya hay datos cargados.'))
            return

        usuarios_data = [
            {'username': 'c4rlosantonio527', 'bio': 'Desarrollador full-stack apasionado por Django y React.', 'location': 'Madrid'},
            {'username': 'gustavoantonich', 'bio': 'Disenador UX / Creador de contenido digital.', 'location': 'Barcelona'},
            {'username': 'techgirl', 'bio': 'Ingeniera de software. Python, Go, e infraestructura cloud.', 'location': 'Valencia'},
            {'username': 'devmaster', 'bio': 'Tech lead con 10+ anos de experiencia. Mentor y speaker.', 'location': 'Sevilla'},
            {'username': 'codewhisperer', 'bio': 'Escribo codigo y a veces funciona a la primera.', 'location': 'Bilbao'},
        ]

        creados = []
        for data in usuarios_data:
            user, created = User.objects.get_or_create(
                username=data['username'],
                defaults={
                    'bio': data['bio'],
                    'location': data['location'],
                    'website': f'https://{data["username"]}.dev',
                }
            )
            if created:
                user.set_password('1234')
                user.save()
            creados.append(user)

        sample_posts = [
            'Acabo de terminar el nuevo diseno de TellMe. Se ve increible!',
            'Alguien mas piensa que Django 5.2 es el mejor release en anos?',
            'Hoy aprendi a optimizar consultas con select_related y prefetch_related. Game changer.',
            'Buenos dias! Nuevo proyecto personal en camino. Pronto comparto mas detalles.',
            'La clave del buen codigo: legibilidad > ingeniosidad. Siempre.',
            'Me encanta como quedaron las cards en el feed. El diseno limpio gana siempre.',
            'Tip del dia: usa type hints en Python. Tu yo del futuro te lo agradecera.',
            'Trabajando en la funcionalidad de mensajeria para TellMe. Pronto disponible!',
            'El cafe es el motor de todo desarrollador. Quien mas?',
            'Refactorizar codigo legacy es como hacer una cirugia a corazon abierto.',
            'Hoy implemente el sistema de likes. Funciona como un reloj suizo.',
            'Me encanta cuando el CSS queda perfecto al primer intento.',
            'Alguien ha probado HTMX con Django? Estoy pensando en integrarlo.',
            'Ultimo commit del dia. Hora de descansar. Nos vemos manana!',
            'La comunidad dev hispanohablante es increible. Siempre aprendiendo de ustedes.',
        ]

        now = timezone.now()
        for i, post_content in enumerate(sample_posts):
            user = creados[i % len(creados)]
            offset = random.randint(0, 7 * 24 * 60)
            Post.objects.get_or_create(
                user=user,
                content=post_content,
                defaults={
                    'created_at': now - timedelta(minutes=offset),
                }
            )

        self.stdout.write(self.style.SUCCESS(
            f'Creados {len(creados)} usuarios y {len(sample_posts)} posts de ejemplo.'
        ))
        self.stdout.write(self.style.SUCCESS('Password para todos: 1234'))
