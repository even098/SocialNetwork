from django.contrib.postgres.search import SearchVector
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from taggit.models import Tag

from chats.serializers import UserSerializer
from posts.models import Post, PostView


class PostSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    views = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ['id', 'user', 'content', 'photo', 'views', 'created_at']
        read_only_fields = fields

    def get_views(self, obj):
        try:
            return PostView.objects.filter(post=obj).count()
        except PostView.DoesNotExist:
            return 0


class PostCreateSerializer(serializers.ModelSerializer):
    tags = serializers.SlugRelatedField(
        many=True,
        read_only=False,
        slug_field='name',
        queryset=Tag.objects.all()
    )

    class Meta:
        model = Post
        fields = ['content', 'photo', 'tags']

    def create(self, validated_data):
        tags = validated_data.pop('tags', [])
        post = Post.objects.create(
            author=self.context['request'].user,
            content=validated_data['content'],
            photo=validated_data.get('photo'),
        )
        if tags:
            post.tags.add(*tags)

        post.search_vector = SearchVector('content')
        post.save()

        return post

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags', [])
        instance.content = validated_data.get('content', instance.content)
        instance.photo = validated_data.get('photo', instance.photo)

        if tags:
            instance.tags.add(*tags)

        instance.save()

        return instance
