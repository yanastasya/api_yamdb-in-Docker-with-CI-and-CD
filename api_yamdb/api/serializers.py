import datetime as dt

from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.shortcuts import get_object_or_404

from reviews.models import Title, Genre, Categorie, Review, Comment
from users.models import User


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Genre."""
    class Meta:
        model = Genre
        fields = ('name', 'slug')
        lookup_field = 'slug'


class CategorieSerializer(serializers.ModelSerializer):
    """Сериалтзатор для модели Categorie."""
    class Meta:
        model = Categorie
        fields = ('name', 'slug')
        lookup_field = 'slug'


class TitleGetSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Title.
    Для GET запросов к эндпоинтам /title/ и /title/id/.
    """

    genre = GenreSerializer(many=True, read_only=True)
    category = CategorieSerializer(read_only=True)
    rating = serializers.IntegerField(
        min_value=0,
        max_value=10,
        read_only=True,
        required=False
    )

    class Meta:
        fields = (
            'id', 'name', 'category', 'genre', 'description', 'year', 'rating'
        )
        model = Title


class TitlePostSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Title.
    Для POST запросов к эндпоинтам /title/ и /title/id/.
    """
    genre = serializers.SlugRelatedField(
        many=True,
        slug_field='slug',
        queryset=Genre.objects.all()
    )
    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Categorie.objects.all()
    )

    class Meta:
        fields = ('id', 'name', 'category', 'genre', 'description', 'year')
        model = Title

    def validate_year(self, value):
        year = dt.date.today().year
        if not (value <= year):
            raise serializers.ValidationError(
                'Год выпуска не может быть больше текущего.'
            )

        return value


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Comment."""
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Review."""
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
    )

    class Meta:
        model = Review
        fields = '__all__'
        read_only_fields = ['title', ]

    def validate(self, data):
        if self.context['request'].method != 'POST':
            return data

        title_id = self.context['view'].kwargs.get('title_id')
        author = self.context['request'].user
        if Review.objects.filter(
                author=author, title=title_id).exists():
            raise serializers.ValidationError(
                'Вы оставляли отзыв на это творение.'
            )
        return data


class UserSerializer(serializers.ModelSerializer):
    role = serializers.ChoiceField(
        choices=User.ROLE_CHOICES,
        required=False,
        error_messages={
            'invalid_choice': (
                'Доступные роли: "user", "moderator", "admin".'
            ),
        },
    )

    class Meta:
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role',
        )
        model = User
        lookup_field = 'username'
        extra_kwargs = {
            'url': {'lookup_field': 'username'}
        }

    def validate_username(self, value):
        if 'me' == value:
            raise serializers.ValidationError("запрещенное имя пользователя")
        return value


class UserMeSerializer(serializers.ModelSerializer):
    role = serializers.ChoiceField(
        choices=User.ROLE_CHOICES,
        required=False,
        read_only=True
    )

    class Meta:
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role',
        )
        model = User
        read_only_fields = ['username', 'email', ]


class SignupSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('username', 'email')
        model = User

    def validate_username(self, value):
        if 'me' == value:
            raise serializers.ValidationError("запрещенное имя пользователя")

        return value


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['confirmation_code'] = serializers.CharField()
        del self.fields['password']

    def validate(self, attrs):
        data = {}
        user = get_object_or_404(User, username=attrs['username'])
        if user.confirmation_code != attrs['confirmation_code']:
            raise serializers.ValidationError("не верный код подверждения.")
        refresh = self.get_token(user)

        data["access"] = str(refresh.access_token)

        return data
