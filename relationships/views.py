from django.contrib.auth import get_user_model
from django.db.models import F
from rest_framework import status, exceptions
from rest_framework.generics import CreateAPIView, DestroyAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from relationships.models import Follow
from relationships.serializers import FollowersSerializer


class FollowUserAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, user_id):
        follower = request.user
        following = get_user_model().objects.filter(id=user_id).first()

        if not following:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        if Follow.objects.filter(follower=follower, following=following).exists():
            return Response({"detail": "You are already following this user."})

        if follower == following:
            return Response({"detail": "You cannot follow yourself."})

        Follow.objects.create(follower=follower, following=following)
        get_user_model().objects.filter(id=follower.id).update(following_count=F('following_count') + 1)
        get_user_model().objects.filter(id=following).update(followers_count=F('followers_count') + 1)
        return Response({"detail": "Successfully followed the user."})


class UnfollowUserAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, user_id):
        following = get_user_model().objects.filter(id=user_id).first()
        follower = request.user

        if not following:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        follow_instance = Follow.objects.filter(follower=follower, following=following).first()

        if follow_instance:
            follow_instance.delete()
            get_user_model().objects.filter(id=following.id).update(followers_count=F('followers_count') - 1)
            get_user_model().objects.filter(id=follower.id).update(following_count=F('following_count') - 1)
            return Response({"message": "Successfully unfollowed the user."}, status=status.HTTP_200_OK)

        return Response({"detail": "You are not following this user."}, status=status.HTTP_400_BAD_REQUEST)


class FollowersListAPIView(ListAPIView):
    serializer_class = FollowersSerializer

    def get_queryset(self, *args, **kwargs):
        user_id = self.kwargs.get('user_id')
        return get_user_model().objects.filter(following__following_id=user_id).prefetch_related('following')


class FollowingListAPIView(ListAPIView):
    serializer_class = FollowersSerializer

    def get_queryset(self, *args, **kwargs):
        user_id = self.kwargs.get('user_id')
        return get_user_model().objects.filter(followers__follower_id=user_id).prefetch_related('followers')
