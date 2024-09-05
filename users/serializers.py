from django.contrib.auth import get_user_model
from rest_framework import serializers, status
from rest_framework.response import Response

from users.models import User


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        exclude = ['id', 'password', 'email', 'is_staff', 'is_superuser', 'is_active', 'groups', 'user_permissions',
                   'last_login', 'first_name', 'last_name']


class UserCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ('username', 'email', 'password', 'full_name', 'avatar', 'date_of_birth', 'bio', 'gender',
                  'location')
        extra_kwargs = {
            'password': {'write_only': True},
            'avatar': {'required': False},
            'bio': {'required': False},
            'location': {'required': False}
        }

    def create(self, validated_data):
        if not get_user_model().objects.filter(email=validated_data['email']).exists():
            user = get_user_model().objects.create_user(
                username=validated_data['username'],
                email=validated_data['email'],
                password=validated_data['password'],
                full_name=validated_data.get('full_name'),
                avatar=validated_data.get('avatar'),
                date_of_birth=validated_data.get('date_of_birth'),
                bio=validated_data.get('bio'),
                gender=validated_data.get('gender'),
                location=validated_data.get('location'),
                is_active=False
            )
            return user

        raise serializers.ValidationError({'message': 'Email already exists'})

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        if password:
            instance.set_password(password)

        for key, value in validated_data.items():
            if getattr(instance, key) != value:
                setattr(instance, key, value)
        instance.save()

        return instance
