from django.http import HttpResponse
from rest_framework import status
from rest_framework.generics import CreateAPIView, UpdateAPIView, DestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from posts.models import Post, Like
from posts.serializers import PostCreateSerializer
from posts.permissions import IsOwner


class PostCreateAPIView(CreateAPIView):
    serializer_class = PostCreateSerializer
    permission_classes = [IsAuthenticated,]


class PostEditAPIView(UpdateAPIView):
    serializer_class = PostCreateSerializer
    permission_classes = [IsAuthenticated, IsOwner,]

    def get_object(self):
        obj = Post.objects.get(id=self.kwargs['post_id'])
        self.check_object_permissions(self.request, obj)
        return obj


class PostDeleteAPIView(DestroyAPIView):
    serializer_class = PostCreateSerializer
    permission_classes = [IsAuthenticated, IsOwner,]

    def get_object(self):
        obj = Post.objects.get(id=self.kwargs['post_id'])
        self.check_object_permissions(self.request, obj)
        return obj


class LikePostAPIView(APIView):
    permission_classes = [IsAuthenticated,]

    def post(self, request, post_id):
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return Response({"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND)

        like, created = Like.objects.get_or_create(user=request.user, post=post)

        if created:
            return Response({"message": "Post liked", "likes_count": post.likes_count()}, status=status.HTTP_200_OK)
        else:
            like.delete()
            return Response({"message": "Post unliked", "likes_count": post.likes_count()}, status=status.HTTP_200_OK)
