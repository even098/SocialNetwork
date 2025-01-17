import uuid

from django.contrib.auth import get_user_model
from django.contrib.postgres.search import SearchVectorField, SearchVector
from django.db import models


class Chat(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, blank=True)
    participants = models.ManyToManyField(get_user_model(), related_name='chats')
    last_message = models.ForeignKey('Message', on_delete=models.SET_NULL, null=True, blank=True, related_name='last_message')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Message(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    chat = models.ForeignKey('Chat', on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='sent_messages')
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)  # Для функционала отметки прочитанности
    search_vector = SearchVectorField(null=True)

    class Meta:
        ordering = ['created_at']

    # def save(self, *args, **kwargs):
    #     self.search_vector = SearchVector('text')
    #     super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.sender}: {self.text}"
