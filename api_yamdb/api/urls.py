from django.urls import include, path
from rest_framework import routers

from .views import (get_update_me, UsersViewSet, signup,
                    get_token, CategoriesViewSet, GenresViewSet,
                    TitlesViewSet, UsersViewSet, ReviewsViewSet,
                    CommentsViewSet)


router = routers.DefaultRouter()
router.register(r'users', UsersViewSet)
router.register(r'titles', TitlesViewSet)
router.register(r'categories', CategoriesViewSet,
                basename='categories')
router.register(r'titles/(?P<title_id>\d+)/reviews',
                ReviewsViewSet, basename='reviews')
router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentsViewSet, basename='comments')

urlpatterns = [
    path('v1/', include(router.urls)),
    path('v1/users/me/', get_update_me, name='me'),
    path('v1/auth/signup/', signup, name='signup'),
    path('v1/auth/token/', get_token, name='gettoken'),
]
