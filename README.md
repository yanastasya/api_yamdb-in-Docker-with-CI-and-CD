# Backend для проекта YaMDb(сервис с отзывами на произведения).
Проект YaMDb собирает отзывы пользователей на произведения. Произведения делятся на категории. Произведению может быть присвоен жанр из списка предустановленных. Добавлять произведения, категории и жанры может только администратор. Пользователи оставляют к произведениям текстовые отзывы и ставят произведению оценку в диапазоне от одного до десяти (целое число); из пользовательских оценок формируется усреднённая оценка произведения — рейтинг (целое число). Пользователи могут оставлять комментарии к отзывам. Добавлять отзывы, комментарии и ставить оценки могут только аутентифицированные пользователи.

Проект упакован в контейнеры и настроены следующие процессы: запуск тестов, обнавление образа проекта на DockerHub, автоматический деплой на боевой сервер при пуше в главную ветку main и отправка сообщения об успешном деплое в Telegram. 

![Здесь видно, что workflow прошел успешно](https://github.com/yanastasya/yamdb_final/actions/workflows/yamdb_workflow.yml/badge.svg)

### Стек технологий:
[![Python](https://img.shields.io/badge/-Python-464646?style=flat-square&logo=Python)](https://www.python.org/)
[![Django](https://img.shields.io/badge/-Django-464646?style=flat-square&logo=Django)](https://www.djangoproject.com/)
[![Django REST Framework](https://img.shields.io/badge/-Django%20REST%20Framework-464646?style=flat-square&logo=Django%20REST%20Framework)](https://www.django-rest-framework.org/)
[![PostgreSQL](https://img.shields.io/badge/-PostgreSQL-464646?style=flat-square&logo=PostgreSQL)](https://www.postgresql.org/)
[![Nginx](https://img.shields.io/badge/-NGINX-464646?style=flat-square&logo=NGINX)](https://nginx.org/ru/)
[![gunicorn](https://img.shields.io/badge/-gunicorn-464646?style=flat-square&logo=gunicorn)](https://gunicorn.org/)
[![docker](https://img.shields.io/badge/-Docker-464646?style=flat-square&logo=docker)](https://www.docker.com/)
[![GitHub%20Actions](https://img.shields.io/badge/-GitHub%20Actions-464646?style=flat-square&logo=GitHub%20actions)](https://github.com/features/actions)
[![Yandex.Cloud](https://img.shields.io/badge/-Yandex.Cloud-464646?style=flat-square&logo=Yandex.Cloud)](https://cloud.yandex.ru/)


# Для разворота проекта на вашем сервере:
1) форкните данный репозитарий
2) на сервере должны быть установлены docker, docker-compose
3) в директории yamdb_final/api_yamdb/ находится файл Dockerfile. Необходимо собрать образ и сохранить их на вашем репозитории DockerHub под соответствующим именем.
3) в файлах docker-compose.yaml (строка 14) и yamdb_workflow.yml (строки 55 и  72) изменить "yanastasya" на ваш username на DockerHub.
4) скопировать файлы docker-compose.yaml и nginx/default.conf из проекта на сервер в home/<ваш_username>/docker-compose.yaml и home/<ваш_username>/nginx/default.conf соответственно.
5) Добавьте в Secrets GitHub Actions переменные окружения для работы базы данных:
  -  DB_ENGINE=django.db.backends.postgresql # указываем, что работаем с postgresql
  -  DB_NAME=postgres # имя базы данных
  -  POSTGRES_USER=postgres # логин для подключения к базе данных
  -  POSTGRES_PASSWORD=qwerty # пароль для подключения к БД (установите свой)
  -  DB_HOST=db # название сервиса (контейнера)
  -  DB_PORT=5432 # порт для подключения к БД
  -  HOST=внешний IP сервера
  -  USER=имя пользователя для подключения к серверу
  -  SSH_KEY=приватный ключ с компьютера, имеющего доступ к боевому серверу
  -  PASSPHRASE=фраза-пароль ,если использовали её при создании ssh-ключа
  -  TELEGRAM_TO = ID своего телеграм-аккаунта.
  -  TELEGRAM_TOKEN = токен вашего бота, который будет присылать сообщение об успешном деплое.
  -  DOCKER_USERNAME и DOCKER_PASSWORD - ваши логин и пароль на докерхаб.
    
6) выполните git push
7) после успешного деплоя зайти на сервер и выполнить команды:
    ```
    sudo docker-compose exec web bash
    python manage.py migrate
    python manage.py collectstatic
    python manage.py createsuperuser
    ```
8) вам будут доступны адреса:
    ``` http://<IP_сервера>/redoc ``` - документация к API 
    ``` http://<IP_сервера>/admin ``` - админка---
