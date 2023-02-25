from django.contrib.auth.models import AbstractUser
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models


class CustomUserManager(BaseUserManager):

    def create_user(self, username, email, password, **extra_fields):
        if not username:
            raise ValueError('Username обязательное поле')
        if not email:
            raise ValueError('Email обязательное поле')
        email = self.normalize_email(email)
        username = self.model.normalize_username(username)
        user = self.model(
            username=username,
            email=email,
            **extra_fields
        )
        if extra_fields.get('is_superuser') is True:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save()

        return user

    def create_superuser(self, username, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'admin')

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(username, email, password, **extra_fields)


class User(AbstractUser):

    USER = 'user'
    MODERATOR = 'moderator'
    ADMIN = 'admin'
    ROLE_CHOICES = [
        (USER, 'user'),
        (MODERATOR, 'moderator'),
        (ADMIN, 'admin'),
    ]
    username_validator = UnicodeUsernameValidator()
    objects = CustomUserManager()

    username = models.CharField(
        max_length=150,
        unique=True,
        help_text='Буквы, цифры and @/./+/-/_ only.',
        validators=[username_validator],
        error_messages={
            'unique': ("Username занят."),
        },
    )
    email = models.EmailField(
        max_length=254,
        unique=True,
        error_messages={'unique': ("почта уже существует."), },
    )
    first_name = models.CharField('Имя', max_length=150, blank=True)
    last_name = models.CharField('Фамилия', max_length=150, blank=True)
    bio = models.TextField('Биография', blank=True)
    confirmation_code = models.CharField(
        'Код подтверждения', max_length=6, blank=True
    )
    role = models.CharField(
        'Роль пользователя',
        max_length=9,
        choices=ROLE_CHOICES,
        default=USER,
        error_messages={
            'invalid_choice': ("роли не существует."),
        },
        blank=True,
    )

    class Meta:
        ordering = ['id']

    def __str__(self):
        return self.username

    @property
    def is_admin_or_super_user(self):
        return self.role == self.ADMIN or self.is_superuser

    @property
    def is_moderator_or_admin_or_super_user(self):
        return (
            self.role == self.MODERATOR or self.is_admin_or_super_user
        )
