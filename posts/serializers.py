from django.contrib.auth import get_user_model
from rest_framework import serializers

from posts.models import Post


class PostCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['title', 'photo']

    def create(self, validated_data):
        post = Post.objects.create(
            author=self.context['request'].user,
            title=validated_data['title'],
            photo=validated_data.get('photo'),
        )
        return post

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.photo = validated_data.get('photo', instance.photo)
        instance.save()
        return instance
