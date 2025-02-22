from django.contrib.postgres.search import SearchQuery, SearchRank
from django.db.models import Q, F

from chats.models import Chat
from posts.models import Post
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


def get_filtered_posts(author=None, keyword=None):
    filters = Q()
    if author:
        filters &= (Q(author__username__icontains=author) | Q(author__full_name__icontains=author))

    if keyword:
        query = SearchQuery(keyword)
        filters &= Q(search_vector=query)
        results = Post.objects.annotate(
            rank=SearchRank(F('search_vector'), query)
        ).filter(filters).order_by('-rank')
    else:
        results = Post.objects.filter(filters)

    return results


def get_filtered_users(keyword=None):
    return User.objects.filter(
        Q(username__icontains=keyword) |
        Q(full_name__icontains=keyword)
    ).distinct()
