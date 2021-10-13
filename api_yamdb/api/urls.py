from django.urls import include, path
from rest_framework import routers

from .views import get_update_me, UsersViewSet, signup, get_token

router = routers.DefaultRouter()
router.register(r'users', UsersViewSet)

urlpatterns = [
    path('v1/', include(router.urls)),
    path('v1/users/me', get_update_me, name='me'),
    path('v1/auth/signup/', signup, name='signup'),
    path('v1/auth/token/', get_token, name='gettoken'),
]
