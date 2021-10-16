from rest_framework import viewsets
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from rest_framework import filters
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from django.contrib.auth.tokens import default_token_generator
from rest_framework_simplejwt.tokens import AccessToken
from django_filters.rest_framework import DjangoFilterBackend

from reviews.models import User, Category, Genre, Title, Comments, Review

from .serializers import (UserSerializer, MeSerializer, SingUpSerializer,
                          CategorySerializer, GenreSerializer, TitlesReadSerializer, TitlesWriteSerializer,
                          CommentSerializer, ReviewSerializer, TokenSerializer)

from .permissions import (IsAdminOrSuperuser, IsAdminUserOrReadOnly,
                          OwnerOrReadOnly, AdminOrModeratorOrRead)


def sent_verification_code(user):
    confirmation_code = default_token_generator.make_token(user)
    send_mail(
        'Код подтверждения',
        f'Ваш код: {confirmation_code}',
        'db_yamdb@example.com',
        [user.email],
        fail_silently=False,
    )


@api_view(['POST'])
def signup(request):
    serializer = SingUpSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        user = User.objects.get_or_create(username=serializer.data['username'],
                                          email=serializer.data['email'])
        user = get_object_or_404(User, username=serializer.data['username'])
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
    if request.user.is_authenticated:
        if request.method == "PATCH":
            me = get_object_or_404(User, id=request.user.id)
            serializer = MeSerializer(me, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)
        me = get_object_or_404(User, id=request.user.id)
        serializer = MeSerializer(me)
        return Response(serializer.data)
    return Response(
        "Пожалуйста авторизуйтесь",
        status=status.HTTP_401_UNAUTHORIZED,
    )


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
    queryset = Title.objects.all()
    permission_classes = (IsAdminUserOrReadOnly,)
    filter_backends = (DjangoFilterBackend, filters.SearchFilter,)
    search_fields = ('slug', 'year', 'name')
    filterset_fields = ('name', 'year', 'genre__slug')

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return TitlesReadSerializer
        return TitlesWriteSerializer


class GenreViewSet(viewsets.ModelViewSet):
    """Вьюсет для жанров"""
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('slug',)
    permission_classes = (IsAdminUserOrReadOnly,)
    search_fields = ('slug', 'name')


@api_view(['DELETE'])
def delete_genre(request, slug):
    genre = get_object_or_404(Genre, slug=slug)
    if request.user.is_authenticated:
        if request.user.role == 'admin':
            genre.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_403_FORBIDDEN)
    return Response(status=status.HTTP_401_UNAUTHORIZED)


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
    if request.user.is_authenticated:
        if request.user.role == 'admin':
            category.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_403_FORBIDDEN)
    return Response(status=status.HTTP_401_UNAUTHORIZED)


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
        title = get_object_or_404(Title, pk=self.kwargs['title_id'])
        reviews = title.reviews.get(pk=self.kwargs['review_id'])
        return reviews.comments.all()

    def perform_create(self, serializer):
        review = get_object_or_404(Review, pk=self.kwargs['review_id'])
        serializer.save(author=self.request.user, review=review)
