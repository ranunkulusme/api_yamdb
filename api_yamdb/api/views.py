from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import api_view
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken

from api_yamdb.settings import EMAIL
from reviews.models import Category, Genre, Review, Title, User

from .filters import TitleFilter
from .permissions import (AdminOrModeratorOrRead, IsAdminOrSuperuser,
                          IsAdminUserOrReadOnly, OwnerOrReadOnly)
from .serializers import (CategorySerializer, CommentSerializer,
                          GenreSerializer, MeSerializer, ReviewSerializer,
                          SingUpSerializer, TitlesReadSerializer,
                          TitlesWriteSerializer, TokenSerializer,
                          UserSerializer)


def sent_verification_code(user):
    confirmation_code = default_token_generator.make_token(user)
    send_mail(
        'Код подтверждения',
        f'Ваш код: {confirmation_code}',
        EMAIL,
        [user.email],
        fail_silently=False,
    )


@api_view(['POST'])
def signup(request):
    serializer = SingUpSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        user, _ = User.objects.get_or_create(
            username=serializer.data['username'],
            email=serializer.data['email'])
        sent_verification_code(user)
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def get_token(request):
    serializer = TokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = get_object_or_404(User, username=serializer.data['username'])
    confirmation_code = serializer.data['confirmation_code']
    if default_token_generator.check_token(user, confirmation_code):
        token = AccessToken.for_user(user)
        return Response(f'{token}', status=status.HTTP_200_OK)
    return Response(
        "Отсутствует обязательное поле или оно некорректно",
        status=status.HTTP_400_BAD_REQUEST,
    )


@api_view(['GET', 'PATCH'])
def get_update_me(request):
    if request.user.is_anonymous:
        return Response(
            "Пожалуйста авторизуйтесь",
            status=status.HTTP_401_UNAUTHORIZED,
        )
    if request.method == "GET":
        me = get_object_or_404(User, id=request.user.id)
        serializer = MeSerializer(me)
        return Response(serializer.data)
    me = get_object_or_404(User, id=request.user.id)
    serializer = MeSerializer(me, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)
    permission_classes = (IsAdminOrSuperuser,)
    lookup_field = "username"
    lookup_value_regex = "[^/]+"


class TitleViewSet(viewsets.ModelViewSet):
    """Вьюсет для произведений"""
    queryset = Title.objects.all().annotate(rating=Avg("reviews__score"))
    permission_classes = (IsAdminUserOrReadOnly,)
    filter_backends = (DjangoFilterBackend, filters.SearchFilter,)
    search_fields = ('slug', 'year', 'name')
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return TitlesReadSerializer
        return TitlesWriteSerializer


class GenreViewSet(viewsets.ModelViewSet):
    """Вьюсет для жанров"""
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    filter_backends = (filters.SearchFilter,)
    permission_classes = (IsAdminUserOrReadOnly,)
    search_fields = ('slug', 'name')


@api_view(['DELETE'])
def delete_genre(request, slug):
    genre = get_object_or_404(Genre, slug=slug)
    if request.user.is_anonymous:
        return Response(status=status.HTTP_401_UNAUTHORIZED)
    if request.user.is_adminisrator:
        genre.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    return Response(status=status.HTTP_403_FORBIDDEN)


class CategoryViewSet(viewsets.ModelViewSet):
    """Вьюсет для категорий"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (OwnerOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('slug', 'name')


@api_view(['DELETE'])
def delete_categories(request, slug):
    category = get_object_or_404(Category,
                                 slug=slug)
    if request.user.is_anonymous:
        return Response(status=status.HTTP_401_UNAUTHORIZED)
    if request.user.is_adminisrator:
        category.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    return Response(status=status.HTTP_403_FORBIDDEN)


class ReviewsViewSet(viewsets.ModelViewSet):
    """
    Вьюсет для отзывов
    """
    serializer_class = ReviewSerializer
    lookup_url_kwarg = 'review_id'
    permission_classes = (AdminOrModeratorOrRead,)

    def get_queryset(self):
        title_id = self.kwargs['title_id']
        titles = get_object_or_404(Title, id=title_id)
        return titles.reviews.all()

    def perform_create(self, serializer):
        title_id = self.kwargs['title_id']
        title = get_object_or_404(Title, pk=title_id)
        serializer.save(author=self.request.user, title=title)


class CommentsViewSet(viewsets.ModelViewSet):
    """
    Вьюсет для комментариев
    """
    serializer_class = CommentSerializer
    lookup_url_kwarg = 'comments_id'
    permission_classes = (AdminOrModeratorOrRead,)

    def get_queryset(self):
        title_id = self.kwargs['title_id']
        review_id = self.kwargs['review_id']
        title = get_object_or_404(Title, pk=title_id)
        try:
            reviews = title.reviews.get(pk=review_id)
        except Review.DoesNotExist:
            raise ValidationError(
                {'detail': (f'Отзыва с ID {review_id} к произведению '
                            f'{title} не существует')}
            )
        return reviews.comments.all()

    def perform_create(self, serializer):
        review = get_object_or_404(Review, pk=self.kwargs['review_id'])
        serializer.save(author=self.request.user, review=review)
