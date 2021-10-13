from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from reviews.models import Users


class UsersSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('username', 'email', 'first_name', 'last_name', 'bio', 'role',)
        model = Users
        lookup_field = 'username'

        validators = [
            UniqueTogetherValidator(
                queryset=Users.objects.all(),
                fields=('username', 'email')
            )
        ]

        def create(self, validated_data):
            return Users.objects.get_or_create(**validated_data)[0]

        def validate(self, data):
            if data['username'] == 'me':
                raise serializers.ValidationError("me - недопустимый username")
            return data


class MeSerializer(serializers.ModelSerializer):
    role = serializers.StringRelatedField(read_only=True)

    class Meta:
        fields = ('username', 'email', 'first_name', 'last_name', 'bio', 'role',)
        model = Users

        validators = [
            UniqueTogetherValidator(
                queryset=Users.objects.all(),
                fields=('username', 'email')
            )
        ]


class SingUpSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ('username', 'email')

        validators = [
            UniqueTogetherValidator(
                queryset=Users.objects.all(),
                fields=('username', 'email')
            )
        ]

    def validate(self, data):
        if data['username'] == 'me':
            raise serializers.ValidationError("me - недопустимый username")
        return data


class TokenSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=100)
    confirmation_code = serializers.CharField(max_length=500)

