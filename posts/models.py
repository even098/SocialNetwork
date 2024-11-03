from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from taggit.managers import TaggableManager
from taggit.models import TaggedItem


class Post(models.Model):
    author = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    photo = models.ImageField(blank=True, null=True, upload_to='posts/photos/')
    tags = TaggableManager()
    tagged_items = GenericRelation(TaggedItem)
    created_at = models.DateTimeField(auto_now_add=True)

    def likes_count(self):
        return self.like_set.count()

    def comments_count(self):
        return self.comments.count()


class Like(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post')
