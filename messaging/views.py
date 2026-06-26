from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages as django_messages
from django.db.models import Q, Count, Max
from django.contrib.auth import get_user_model
from .models import Conversation, Message

User = get_user_model()


@login_required
def inbox_view(request):
    conversations = Conversation.objects.filter(participants=request.user).annotate(
        last_message_time=Max("messages__created_at"),
        unread_count=Count("messages", filter=Q(messages__is_read=False) & ~Q(messages__sender=request.user)),
    ).order_by("-last_message_time")

    return render(request, "messaging/inbox.html", {
        "conversations": conversations,
    })


@login_required
def conversation_view(request, conversation_id):
    conversation = get_object_or_404(
        Conversation.objects.filter(participants=request.user),
        id=conversation_id,
    )
    other = conversation.participants.exclude(id=request.user.id).first()

    if request.method == "POST":
        content = request.POST.get("content", "").strip()
        if content:
            Message.objects.create(
                conversation=conversation,
                sender=request.user,
                content=content,
            )
        return redirect("conversation", conversation_id=conversation.id)

    messages_list = conversation.messages.select_related("sender").all()

    conversation.messages.filter(~Q(sender=request.user), is_read=False).update(is_read=True)

    return render(request, "messaging/conversation.html", {
        "conversation": conversation,
        "other": other,
        "messages": messages_list,
    })


@login_required
def start_conversation_view(request, username):
    other = get_object_or_404(User, username=username)
    if other == request.user:
        return redirect("inbox")

    conversation = Conversation.objects.filter(participants=request.user).filter(participants=other).first()
    if not conversation:
        conversation = Conversation.objects.create()
        conversation.participants.add(request.user, other)

    return redirect("conversation", conversation_id=conversation.id)
