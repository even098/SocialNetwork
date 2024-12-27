from rest_framework.generics import ListAPIView, CreateAPIView, ListCreateAPIView
from rest_framework.permissions import IsAuthenticated


from chats.models import Chat
from chats.serializers import ChatSerializer


class ChatsAPIView(ListCreateAPIView):
    serializer_class = ChatSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Chat.objects.filter(participants=self.request.user)
