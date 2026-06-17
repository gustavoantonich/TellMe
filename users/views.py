from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.core.mail import send_mail
from django.conf import settings
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.contrib import messages
from .forms import RegisterForm, LoginForm, EditProfileForm
from .models import User
from posts.models import Post


def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.is_active = True
            user.save()
            _send_verification_email(request, user)
            login(request, user)
            messages.success(
                request,
                "Te enviamos un correo de verificación. Revisa tu bandeja de entrada."
            )
            return redirect("profile", username=user.username)
    else:
        form = RegisterForm()

    return render(request, "users/register.html", {"form": form})


def _send_verification_email(request, user):
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    link = request.build_absolute_uri(
        f"/users/verify-email/{uid}/{token}/"
    )
    send_mail(
        subject="Verifica tu correo electrónico - TellMe",
        message=(
            f"Hola {user.username},\n\n"
            f"Gracias por registrarte en TellMe.\n"
            f"Verifica tu correo haciendo clic en este enlace:\n{link}\n\n"
            f"Si no creaste esta cuenta, ignora este mensaje."
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=True,
    )


@login_required
def send_verification_email_view(request):
    if request.user.is_email_verified:
        messages.info(request, "Tu correo ya está verificado.")
    else:
        _send_verification_email(request, request.user)
        messages.success(request, "Correo de verificación enviado.")
    return redirect("profile", username=request.user.username)


def verify_email_view(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user and default_token_generator.check_token(user, token):
        user.is_email_verified = True
        user.save()
        messages.success(request, "Correo verificado correctamente.")
        return redirect("profile", username=user.username)

    messages.error(request, "El enlace de verificación no es válido o ha expirado.")
    return redirect("login")


def login_view(request):
    if request.method == "POST":
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("profile", username=user.username)
    else:
        form = LoginForm()

    return render(request, "users/login.html", {"form": form})


def profile_view(request, username):
    profile = get_object_or_404(
        User.objects.annotate(
            followers_count=Count("followers", distinct=True),
            following_count=Count("following", distinct=True),
            posts_count=Count("posts", distinct=True),
        ),
        username=username,
    )

    posts = (
        Post.objects.filter(user=profile, parent=None)
        .select_related("user")
        .annotate(
            likes_count=Count("like", distinct=True),
            retweets_count=Count("retweets", distinct=True),
            replies_count=Count("replies", distinct=True),
        )
        .order_by("-created_at")
    )

    is_following = False
    if request.user.is_authenticated and request.user != profile:
        is_following = profile.followers.filter(
            follower=request.user
        ).exists()

    return render(request, "users/profile.html", {
        "profile": profile,
        "posts": posts,
        "posts_count": profile.posts_count,
        "followers_count": profile.followers_count,
        "following_count": profile.following_count,
        "is_following": is_following,
    })


@login_required
def edit_profile_view(request):
    user = request.user

    if request.method == "POST":
        form = EditProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect("profile", username=user.username)
    else:
        form = EditProfileForm(instance=user)

    return render(request, "users/edit_profile.html", {
        "form": form,
    })


def logout_view(request):
    logout(request)
    return redirect("login")
