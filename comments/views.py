from rest_framework import status
from rest_framework.generics import ListAPIView, UpdateAPIView, CreateAPIView, DestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from comments.models import Comment
from comments.serializers import CommentsSerializer
from comments.permissions import IsOwner
from comments.models import Like


class CommentListAPIView(ListAPIView):
    model = Comment
    serializer_class = CommentsSerializer

    def get_queryset(self):
        post_id = self.kwargs['post_id']
        return Comment.objects.filter(id=post_id)


class CommentCreateAPIView(CreateAPIView):
    model = Comment
    serializer_class = CommentsSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['post_id'] = self.kwargs['post_id']
        return context


class CommentUpdateAPIView(UpdateAPIView):
    model = Comment
    serializer_class = CommentsSerializer
    permission_classes = [IsAuthenticated, IsOwner]

    def get_object(self):
        post_id = self.kwargs.get('post_id')
        return Comment.objects.get(post_id=post_id)


class CommentDeleteAPIView(DestroyAPIView):
    model = Comment
    serializer_class = CommentsSerializer
    permission_classes = [IsAuthenticated, IsOwner]

    def get_object(self):
        post_id = self.kwargs.get('post_id')
        return Comment.objects.get(post_id=post_id)


class LikeCommentAPIView(APIView):
    permission_classes = [IsAuthenticated,]

    def post(self, request, comment_id):
        try:
            comment = Comment.objects.get(id=comment_id)
        except Comment.DoesNotExist:
            return Response({"error": "Comment not found"}, status=status.HTTP_404_NOT_FOUND)

        like, created = Like.objects.get_or_create(user=request.user, comment=comment)

        if created:
            return Response({"message": "Comment liked", "likes_count": comment.likes_count()},
                            status=status.HTTP_200_OK)
        else:
            like.delete()
            return Response({"message": "Comment unliked", "likes_count": comment.likes_count()},
                            status=status.HTTP_200_OK)
