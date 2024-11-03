from rest_framework import serializers

from posts.models import Post


class PostCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['title', 'photo', 'tags']

    def create(self, validated_data):
        tags = validated_data.pop('tags', [])
        post = Post.objects.create(
            author=self.context['request'].user,
            title=validated_data['title'],
            photo=validated_data.get('photo'),
        )
        if tags:
            post.tags.add(*tags)
        return post

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags', [])
        instance.title = validated_data.get('title', instance.title)
        instance.photo = validated_data.get('photo', instance.photo)

        if tags:
            instance.tags.add(*tags)

        instance.save()

        return instance
