from rest_framework import viewsets
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.validators import UniqueTogetherValidator
from rest_framework import filters
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from django.contrib.auth.tokens import default_token_generator
from rest_framework_simplejwt.tokens import AccessToken

from reviews.models import Users, Categories, Genres, Titles,  Comments, Reviews

from .serializers import (UsersSerializer, MeSerializer, SingUpSerializer, TokenSerializer,
                          CategoriesSerializer, GenresSerializer, TitlesSerializer,
                          CommentSerializer, ReviewSerializer)

from .permissions import IsAdmin, Me, IsAdminUserOrReadOnly


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
        user = Users.objects.get_or_create(username=serializer.data['username'],
                                           email=serializer.data['email'])
        user = get_object_or_404(Users, username=serializer.data['username'])
        sent_verification_code(user)
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def get_token(request):
    serializer = TokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = get_object_or_404(Users, username=serializer.data['username'])
    confirmation_code = serializer.data['confirmation_code']
    if default_token_generator.check_token(user, confirmation_code):
        token = AccessToken.for_user(request.user)
        return Response(f'token: {token}', status=status.HTTP_200_OK)
    return Response(
        "Отсутствует обязательное поле или оно некорректно",
        status=status.HTTP_400_BAD_REQUEST,
    )


@api_view(['GET', 'PATCH'])
def get_update_me(request):
    if request.method == "PATCH":
        me = get_object_or_404(Users, id=request.user.id)
        serializer = MeSerializer(me, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    me = get_object_or_404(Users, id=request.user.id)
    serializer = MeSerializer(me)
    return Response(serializer.data)


class UsersViewSet(viewsets.ModelViewSet):
    queryset = Users.objects.all()
    serializer_class = UsersSerializer
    pagination_class = PageNumberPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)
    permission_classes = (IsAdmin,)
    lookup_field = "username"
    lookup_value_regex = "[^/]+"


class TitlesViewSet(viewsets.ModelViewSet):
    """Вьюсет для произведений"""
    queryset = Titles.objects.all()
    serializer_class = TitlesSerializer
    permission_classes = (IsAdminUserOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('slug', 'year', 'name')


class GenresViewSet(viewsets.ModelViewSet):
    """Вьюсет для жанров"""
    queryset = Genres.objects.all()
    serializer_class = GenresSerializer
    permission_classes = (IsAdminUserOrReadOnly,)


class CategoriesViewSet(viewsets.ModelViewSet):
    """Вьюсет для категорий"""
    queryset = Categories.objects.all()
    serializer_class = CategoriesSerializer
    permission_classes = (IsAdminUserOrReadOnly,)


class ReviewsViewSet(viewsets.ModelViewSet):
    """
    Вьюсет для отзывов
    """
    serializer_class = ReviewSerializer
    lookup_url_kwarg = 'review_id'

    def get_queryset(self):
        title_id = self.kwargs['title_id']
        titles = get_object_or_404(Titles, id=title_id)
        return titles.reviews.all()

    def perform_create(self, serializer):
        title_id = self.kwargs['title_id']
        serializer.save(author=self.request.user, title_id=title_id)


class CommentsViewSet(viewsets.ModelViewSet):
    """
    Вьюсет для комментариев
    """
    serializer_class = CommentSerializer
    pagination_class = PageNumberPagination
    lookup_url_kwarg = 'comments_id'

    def get_queryset(self):
        title = get_object_or_404(Titles, pk=self.kwargs['title_id'])
        reviews = title.reviews.get(pk=self.kwargs['review_id'])
        return reviews.comments.all()

    def perform_create(self, serializer):
        review = get_object_or_404(Reviews, pk=self.kwargs['review_id'])
        serializer.save(author=self.request.user, review=review)





