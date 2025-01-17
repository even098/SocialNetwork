from django.db.models import Q

from chats.models import Chat
from users.models import User


def get_filtered_chats(user, name=None, users=None):
    filters = Q()

    if users:
        users = users.split(',')
    if name:
        filters &= Q(name__icontains=name)
    if users:
        filters &= Q(participants__username__in=users)

    return Chat.objects.filter(participants=user).filter(filters).distinct()


def get_filtered_users(keyword=None):
    return User.objects.filter(
        Q(username__icontains=keyword) |
        Q(full_name__icontains=keyword)
    ).distinct()
