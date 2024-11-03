from django.db.models import Count
from taggit.models import Tag

from posts.models import Post


def recommend_posts_for_user(user, num_recommendations=5):
    user_posts = Post.objects.filter(like__user=user).values_list('id', flat=True)
    user_tags = Tag.objects.filter(taggit_taggeditem_items__object_id__in=user_posts,
                                   taggit_taggeditem_items__content_type__model='post').distinct()
    recommended_posts = Post.objects \
                            .filter(tags__in=user_tags) \
                            .exclude(like__user=user) \
                            .annotate(tag_count=Count('tags')) \
                            .order_by('-tag_count')[:num_recommendations]
    return recommended_posts
