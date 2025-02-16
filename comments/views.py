from rest_framework import status
from rest_framework.generics import ListAPIView, UpdateAPIView, CreateAPIView, DestroyAPIView, get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from comments.models import Comment
from comments.serializers import CommentsSerializer
from comments.permissions import IsOwner
from comments.models import Like
from posts.models import Post


class CommentCreateAPIView(CreateAPIView):
    model = Comment
    serializer_class = CommentsSerializer
    permission_classes = [IsAuthenticated]


class CommentUpdateAPIView(UpdateAPIView):
    model = Comment
    serializer_class = CommentsSerializer
    permission_classes = [IsAuthenticated, IsOwner]

    def get_object(self):
        comment_id = self.kwargs.get('comment_id')
        comment = Comment.objects.get(id=comment_id)
        self.check_object_permissions(self.request, comment)
        return comment


class CommentDeleteAPIView(DestroyAPIView):
    model = Comment
    serializer_class = CommentsSerializer
    permission_classes = [IsAuthenticated, IsOwner]

    def get_object(self):
        comment_id = self.kwargs.get('comment_id')
        comment = Comment.objects.get(id=comment_id)
        self.check_object_permissions(self.request, comment)
        return comment


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
