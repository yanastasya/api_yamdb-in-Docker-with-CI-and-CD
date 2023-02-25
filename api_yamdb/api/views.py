from rest_framework import viewsets
from rest_framework import mixins
from rest_framework import filters
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.utils.crypto import get_random_string
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Avg

from reviews.models import Title, Genre, Categorie, Review
from users.models import User
from .serializers import GenreSerializer, CategorieSerializer
from .serializers import TitleGetSerializer, TitlePostSerializer
from .serializers import (
    CommentSerializer,
    ReviewSerializer,
    UserSerializer,
    UserMeSerializer,
    CustomTokenObtainPairSerializer,
    SignupSerializer
)
from .filters import TitleFilter
from .permissions import (
    IsAdmimOrReadOnly,
    IsAdmimOrModeratorOrReadOnly,
    IsAdminOrSuperUser
)


class CategorieViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    """Эндпоинт  api/v1/categories/.
    GET запрос: Получение списка всех категорий.
    Права доступа: Доступно без токена. Поиск по названию категории.
    POST запрос: Создать категорию. Права доступа: Администратор.
    Поле slug каждой категории должно быть уникальным.
    DEL запрос на api/v1/genres/slug/ удаляет админ.
    """
    queryset = Categorie.objects.all()
    serializer_class = CategorieSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'
    permission_classes = [IsAdmimOrReadOnly]


class GenreViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    """Эндпоинт  api/v1/genres/.
    GET запрос: Получение списка всех жанров.
    Права доступа: Доступно без токена. Поиск по названию жанра.
    POST запрос: Создать жанр. Права доступа: Администратор.
    Поле slug каждого жанра должно быть уникальным.
    DEL запрос на api/v1/genres/slug/ удаляет админ.
    """
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'
    permission_classes = [IsAdmimOrReadOnly]


class TitleViewSet(viewsets.ModelViewSet):
    """"Эндпоинт api/v1/titles/.
    GET: Получить список всех объектов.+ Права доступа: Доступно без токена.
    фильтры по genre__slug  и category__slug, name и year.
    POST:Добавить новое произведение. Права доступа: Администратор.
    Нельзя добавлять произведения, которые еще не вышли.
    При добавлении нового произведения требуется указать уже существующие
    category и genre.
    Эндпоинт api/v1/titles/id:
    GET: получение инфы об объекте. genre кортежем, category как объект.
    Доступно любому пользователю.
    PATCH: получение инфы о произведении по id.
    Доступно только администратору.
    DEL: удаление произведения по id - только администратор.
    """
    queryset = Title.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter
    permission_classes = [IsAdmimOrReadOnly]

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return TitleGetSerializer

        return TitlePostSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        avg = Review.objects.filter(title=instance).aggregate(Avg('score'))
        instance.rating = avg['score__avg']
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class CommentViewSet(viewsets.ModelViewSet):
    """Эндпоинт /api/v1/titles/{title_id}/reviews/{review_id}/comments/.
    GET запрос: Получить список всех комментариев к отзыву по id.
    Права доступа: Доступно без токена.
    POST запрос: Добавить новый комментарий для отзыва.
    Права доступа: Аутентифицированные пользователи.
    Эндпоинт /titles/{title_id}/reviews/{review_id}/comments/{comment_id}/.
    GET запрос: Получить комментарий для отзыва по id.
    Права доступа: Доступно без токена.
    PATCH и DEL запросы: частичное изменение или удаление комментария по id.
    Права доступа: Автор отзыва, модератор или администратор.
    """
    serializer_class = CommentSerializer
    permission_classes = [IsAdmimOrModeratorOrReadOnly]

    def get_queryset(self):
        review = get_object_or_404(
            Review,
            id=self.kwargs.get('review_id')
        )
        return review.comments.all()

    def perform_create(self, serializer):
        review = get_object_or_404(
            Review,
            id=self.kwargs.get('review_id')
        )
        serializer.save(author=self.request.user, review=review)


class ReviewViewSet(viewsets.ModelViewSet):
    """Эндпоинт /api/v1/titles/{title_id}/reviews/.
    GET запрос: получение списка всех отзывов. Доступно без токена.
    POST запрос: добавить новый отзыв. Пользователь может оставить
    только один отзыв на произведение.
    Права доступа: Аутентифицированные пользователи.
    Эндпоинт /api/v1/titles/{title_id}/reviews/{review_id}/.
    GET запрос: Получить отзыв по id для указанного произведения.
    Права доступа: Доступно без токена.
    PATCH и DEL запросы: частичное изменение или удаление отзыва по id.
    Права доступа: Автор отзыва, модератор или администратор.
    """
    serializer_class = ReviewSerializer
    permission_classes = [IsAdmimOrModeratorOrReadOnly]

    def get_queryset(self):
        title = get_object_or_404(
            Title,
            id=self.kwargs.get('title_id'))
        return title.reviews.all()

    def perform_create(self, serializer):
        title = get_object_or_404(
            Title,
            id=self.kwargs.get('title_id'))
        serializer.save(author=self.request.user, title=title)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'username'
    permission_classes = [IsAdminOrSuperUser, ]


class UserMeViewSet(
        mixins.RetrieveModelMixin,
        mixins.UpdateModelMixin,
        viewsets.GenericViewSet
):
    queryset = User.objects.all()
    serializer_class = UserMeSerializer

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        obj = queryset.get(username=self.request.user.username)
        self.check_object_permissions(self.request, obj)

        return obj


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [AllowAny, ]


class SignupViewSet(
    mixins.CreateModelMixin,
    viewsets.GenericViewSet
):
    queryset = User.objects.all()
    serializer_class = SignupSerializer
    permission_classes = [AllowAny, ]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            email = serializer.initial_data['email']
            username = serializer.initial_data['username']
        except KeyError:
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)

            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED,
                headers=headers
            )

        if not User.objects.filter(username=username, email=email).exists():
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)

            return Response(
                serializer.data,
                status=status.HTTP_200_OK,
                headers=headers
            )
        confirmation_code = get_random_string(
            length=settings.CONFIRMATION_CODE_LENGTH
        )
        User.objects.filter(
            username=username
        ).update(confirmation_code=confirmation_code)
        send_mail(
            'Ваш код подтверждения ',
            f'"confirmation_code": "{confirmation_code}" ',
            settings.EMAIL_SENDER,
            [f'{email}'],
            fail_silently=False,
        )
        headers = self.get_success_headers(serializer.initial_data)

        return Response(
            serializer.initial_data,
            status=status.HTTP_200_OK,
            headers=headers
        )

    def perform_create(self, serializer):
        email = serializer.validated_data['email']
        confirmation_code = get_random_string(
            length=settings.CONFIRMATION_CODE_LENGTH
        )
        send_mail(
            'Ваш код подтверждения ',
            f'"confirmation_code": "{confirmation_code}" ',
            settings.EMAIL_SENDER,
            [f'{email}'],
            fail_silently=False,
        )
        serializer.save(confirmation_code=confirmation_code)
