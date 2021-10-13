from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from reviews.models import Users, Categories, Genres, Titles, Comments, Reviews


class UsersSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('username', 'email', 'first_name', 'last_name', 'bio', 'role',)
        model = Users
        lookup_field = 'username'

        def create(self, validated_data):
            return Users.objects.get_or_create(**validated_data)[0]

        def validate(self, data):
            if data['username'] == 'me':
                raise serializers.ValidationError("me - недопустимый username")
            return data

        def __str__(self):
            return self.username


class MeSerializer(serializers.ModelSerializer):
    role = serializers.StringRelatedField(read_only=True)

    class Meta:
        fields = ('username', 'email', 'first_name', 'last_name', 'bio', 'role',)
        model = Users


class SingUpSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ('username', 'email')

    def validate(self, data):
        if data['username'] == 'me':
            raise serializers.ValidationError("me - недопустимый username")
        return data


class TokenSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=100)
    confirmation_code = serializers.CharField(max_length=500)


class GenresSerializer(serializers.ModelSerializer):
    """Сериализатор для жанров"""
    id = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Genres
        fields = ('id', 'title', 'slug')

    def __str__(self):
        return f'{self.slug}', f'{self.title}'


class CategoriesSerializer(serializers.ModelSerializer):
    """Сериализатор для категорий"""
    id = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Categories
        fields = ('id', 'title', 'slug')

    def __str__(self):
        return self.title, self.slug


class TitlesSerializer(serializers.ModelSerializer):
    """Сериализатор для произведений"""
    author = serializers.HiddenField(default=serializers.CurrentUserDefault())
    genre = GenresSerializer(required=False)
    category = CategoriesSerializer(required=False)

    class Meta:
        model = Titles
        fields = ('id', 'name', 'year', 'description', 'author', 'genre',
                  'category')
        read_only_fields = ('author',)

    def __str__(self):
        return self.name


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = Reviews
        fields = ('id', 'text', 'author', 'score', 'pub_date')

        # validators = [
        #     UniqueTogetherValidator(
        #         queryset=Reviews.objects.all(),
        #         fields=('author', 'title_id'),
        #     )
        # ]

    def create(self, validated_data):
        title_id = validated_data.pop('title_id')
        reviews = Reviews.objects.update_or_create(
            title_id=Titles.objects.get(id=title_id),
            **validated_data
        )
        return reviews


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = Comments
        fields = ('id', 'text', 'author', 'pub_date',)
        read_only_fields = ('author',)




