from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.indexes import GinIndex
from django.db import models
from django.forms import EmailField


class User(AbstractUser):
    email = models.EmailField(unique=True, null=False, blank=False)
    full_name = models.CharField(max_length=255, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    bio = models.TextField(max_length=100, blank=True, null=True)
    gender = models.CharField(
        max_length=10,
        choices=[('M', 'male'), ('F', 'Female'), ('O', 'Other')],
        blank=True
    )
    location = models.CharField(max_length=255, blank=True)
    followers_count = models.PositiveIntegerField(default=0)
    following_count = models.PositiveIntegerField(default=0)
    last_login = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.username
