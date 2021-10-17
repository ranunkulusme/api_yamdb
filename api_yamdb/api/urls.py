from django.urls import include, path
from rest_framework import routers

from .views import (CategoryViewSet, CommentsViewSet, GenreViewSet,
                    ReviewsViewSet, TitleViewSet, UserViewSet,
                    delete_categories, delete_genre, get_token, get_update_me,
                    signup)

router = routers.DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'titles', TitleViewSet)
router.register(r'categories', CategoryViewSet,
                basename='categories')
router.register(r'genres', GenreViewSet,
                basename='categories')
router.register(r'titles/(?P<title_id>\d+)/reviews',
                ReviewsViewSet, basename='reviews')
router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentsViewSet, basename='comments')

urlpatterns = [
    path('v1/', include([
        path('users/me/', get_update_me, name='me'),
        path('categories/<slug:slug>/', delete_categories,
             name='delete_categories'),
        path('genres/<slug:slug>/', delete_genre, name='delete_genre'),
        path('auth/signup/', signup, name='signup'),
        path('auth/token/', get_token, name='gettoken'),
        path('', include(router.urls)),
    ]))
]
