# FOODGRAM_PROJECT
![example branch parameter](https://github.com/SoliDeoGloriaaa/yamdb_final/actions/workflows/yamdb_workflow.yml/badge.svg)

Сайт ```Foodgram```, «Продуктовый помощник». На этом сервисе пользователи смогут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.
IP сервера - 158.160.23.165

## Учётные данные для входа в админку для ревьюера =)
email: admin@mailr.u
password: admin


## Технологии и их версии
В проекте использовались такие технологии, как:
- Django==2.2.19
- pytz==2023.3
- sqlparse==0.4.4
- asgiref==3.2.10
- django-filter==2.4.0
- djangorestframework==3.12.4
- djangorestframework-simplejwt==4.8.0
- gunicorn==20.0.4
- psycopg2-binary==2.8.6
- PyJWT==2.1.0
- pytest-django
- pytest-pythonpath
- djoser==2.1.0
- jango-colorfield==0.7.2
- drf-extra-fields==3.4.0
- drf-yasg==1.21.3
- django-rest-swagger==2.2.0
- python-dotenv==0.21.0


## Авторы
Над проектом работал студент Backend факультета Яндекс.Практикум:
+ [Александр](https://github.com/SoliDeoGloriaaa)


## Как запустить проект пользователям системы Windows
1. Проверьте, установлен ли у вас Docker на компьютере
```
docker -v
```

2. Клонировать репозиторий командой
```
git clone git@github.com:SoliDeoGloriaaa/yamdb_final.git
```

3. Запустить ```docker-compose```
    Выполнить команду
    ```
    docker-compose up -d
    ```

4. Выполнить миграции
```
docker-compose exec web python manage.py migrate
```

5. Прогрузить статику
```
docker-compose exec web python manage.py collectstatic
```

## Шаблон наполнения .env файла расположенный по пути infra/.env
```
DB_ENGINE=django.db.backends.postgresql # указываем, что работаем с postgresql
DB_NAME=postgres                        # имя базы данных
POSTGRES_USER=postgres                  # логин для подключения к базе данных
POSTGRES_PASSWORD=postgres              # пароль для подключения к БД (установите свой)
DB_HOST=db                              # название сервиса (контейнера)
DB_PORT=5432                            # порт для подключения к БД 
```

## Примеры запросов к API

Документацию к API можно посмотреть на запущенном сервере через путь `/redoc/`
