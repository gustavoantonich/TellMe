from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Post


@login_required
def feed(request):
    posts = Post.objects.select_related('author').all()

    return render(
        request,
        'posts/feed.html',
        {'posts': posts}
    )


@login_required
def create_post(request):

    if request.method == 'POST':

        content = request.POST.get('content')

        if content:

            Post.objects.create(
                author=request.user,
                content=content
            )

        return redirect('feed')

    return redirect('feed')
#Añadido 7 c4