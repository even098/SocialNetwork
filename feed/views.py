from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from feed.post_recommendation import recommend_posts_for_user


class RecommendPostsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        recommended_posts = recommend_posts_for_user(user)

        posts_data = [
            {
                'id': post.id,
                'title': post.title,
                'photo': post.photo.url if post.photo else None,
                'tags': [tag.name for tag in post.tags.all()]
            }
            for post in recommended_posts
        ]

        return Response(posts_data)
