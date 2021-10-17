import datetime

from rest_framework import serializers

from reviews.models import Category, Comments, Genre, Review, Title, User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role',)
        model = User
        lookup_field = 'username'

        def __str__(self):
            return self.username


class MeSerializer(serializers.ModelSerializer):
    role = serializers.StringRelatedField(read_only=True)

    class Meta:
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role',)
        model = User


class SingUpSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email')

    def validate_username(self, value):
        """
        Check that username is not me.
        """
        if 'me' == value:
            raise serializers.ValidationError("me - invalid name")
        return value


class TokenSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=100)
    confirmation_code = serializers.CharField(max_length=500)


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор для жанров"""
    id = serializers.IntegerField(write_only=True, required=False)

    class Meta:
        model = Genre
        fields = ('id', 'name', 'slug')

    def __str__(self):
        return f'{self.slug}', f'{self.name}'


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для категорий"""
    id = serializers.IntegerField(write_only=True, required=False)

    class Meta:
        model = Category
        fields = ('id', 'name', 'slug')

    def __str__(self):
        return self.name, self.slug


class TitlesWriteSerializer(serializers.ModelSerializer):
    """Сериализатор для записи произведений"""
    genre = serializers.SlugRelatedField(slug_field='slug', many=True,
                                         queryset=Genre.objects.all())
    category = serializers.SlugRelatedField(slug_field='slug',
                                            queryset=Category.objects.all())

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'description',
                  'genre', 'category')

    def validate_year(self, value):
        current_year = datetime.datetime.now().year
        if 0 > value > current_year:
            raise serializers.ValidationError(
                'Год выпуска не может быть больше текущего года, или меньше 0'
            )
        return value


class TitlesReadSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения произведений"""
    genre = GenreSerializer(required=False, many=True)
    category = CategorySerializer(required=False)
    rating = serializers.IntegerField(read_only=True, required=False)

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'rating', 'description',
                  'genre', 'category')

    def __str__(self):
        return self.name


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
        default=serializers.CurrentUserDefault()
    )
    score = serializers.IntegerField(max_value=10, min_value=0)

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date',)

    def validate(self, data):
        user = self.context['request'].user
        title_id = self.context['request'].parser_context['kwargs']['title_id']
        action_method = self.context['request'].method

        reviews = Review.objects.filter(
            author=user).filter(title_id=title_id).exists()
        if reviews and action_method == 'POST':
            raise serializers.ValidationError(
                'Нельзя дважды оставить отзыва на одно и тоже произведение'
            )
        return data


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
