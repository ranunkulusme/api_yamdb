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

    def validate(self, data):
        if data['username'] == 'me':
            raise serializers.ValidationError("me - недопустимый username")
        return data


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

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date',)

    def validate(self, data):
        if not 0 <= data['score'] <= 10:
            raise serializers.ValidationError(
                'Поставьте оценку от 0 до 10'
            )
        user = self.context['request'].user

        reviews = Review.objects.filter(author=user)
        titles_id_user = [review.title_id for review in reviews]
        title_id = self.context['request'].parser_context['kwargs']['title_id']
        action_method = self.context['request'].method
        if int(title_id) in titles_id_user and action_method == 'POST':
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
