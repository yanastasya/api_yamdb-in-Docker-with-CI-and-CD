from api.views import (CustomTokenObtainPairView, SignupViewSet, UserMeViewSet,
                       UserViewSet)
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (CategorieViewSet, CommentViewSet, GenreViewSet,
                    ReviewViewSet, TitleViewSet)

app_name = 'api'

v1_router = DefaultRouter()


v1_router.register(r'users', UserViewSet, basename='users')
v1_router.register('titles', TitleViewSet, basename='titles')
v1_router.register('genres', GenreViewSet, basename='genres')
v1_router.register('categories', CategorieViewSet, basename='categories')
v1_router.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewViewSet,
    basename='reviews'
)
v1_router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet,
    basename='comments'
)

urlpatterns = [
    path(
        r'v1/users/me/',
        UserMeViewSet.as_view({'get': 'retrieve', 'patch': 'update'}),
        name='user_me'
    ),
    path(
        r'v1/auth/signup/',
        SignupViewSet.as_view({'post': 'create'}),
        name='signup'
    ),
    path(
        r'v1/auth/token/',
        CustomTokenObtainPairView.as_view(),
        name='token_obtain_pair'
    ),
    path(r'v1/', include(v1_router.urls)),
]
