from django.shortcuts import get_object_or_404
from rest_framework import serializers

from chats.serializers import UserSerializer
from comments.models import Comment
from posts.models import Post


class CommentsSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    post_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'text', 'user', 'post_id']
        read_only_fields = ['id', 'user']

    def create(self, validated_data):
        post_id = validated_data.get('post_id')
        post = get_object_or_404(Post, id=post_id)

        comment = Comment.objects.create(
            text=validated_data.get('text'),
            user=self.context['request'].user,
            post=post
        )
        return comment

    def update(self, instance, validated_data):
        instance.text = validated_data.get('text', instance.text)
        instance.save()
        return instance
