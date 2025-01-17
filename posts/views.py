from django.http import HttpResponse
from rest_framework import status
from rest_framework.generics import CreateAPIView, UpdateAPIView, DestroyAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from comments.models import Comment
from comments.serializers import CommentsSerializer
from posts.models import Post, Like, PostView
from posts.serializers import PostCreateSerializer, PostSerializer
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


class PostCommentListAPIView(APIView):
    def get(self, request, post_id):
        try:
            post = Post.objects.get(id=post_id)
            serialized_post = PostSerializer(post).data
            comments = Comment.objects.filter(post=post)
            serialized_comments = CommentsSerializer(comments, many=True).data
            PostView.objects.create(post=post, user=request.user)
            return Response(data={'post': serialized_post, 'comments': serialized_comments}, status=status.HTTP_200_OK)
        except Post.DoesNotExist:
            return Response(data={'error': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)
