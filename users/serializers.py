from django.contrib.auth import get_user_model
from rest_framework import serializers, status


UserModel = get_user_model()


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = ['username', 'full_name', 'avatar', 'date_of_birth', 'bio', 'gender', 'location', 'followers_count',
                  'following_count']


class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = ['username', 'email', 'password', 'full_name', 'avatar', 'date_of_birth', 'bio', 'gender',
                  'location']
        extra_kwargs = {
            'avatar': {'required': False},
            'bio': {'required': False},
            'location': {'required': False}
        }

    def create(self, validated_data):
        if not UserModel.objects.filter(email=validated_data['email']).exists():
            user = UserModel.objects.create_user(
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


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = ['username', 'email', 'full_name', 'avatar', 'date_of_birth', 'bio', 'gender', 'location']
        read_only_fields = ['email', 'date_of_birth', 'gender']

    def update(self, instance, validated_data):
        for key, value in validated_data.items():
            if getattr(instance, key) != value:
                setattr(instance, key, value)
        instance.save()
        return instance
