![example workflow](https://github.com/epsilonm/foodgram-project-react/actions/workflows/main.yml/badge.svg)
# Продуктовый помощник



**«Продуктовый помощник»**: сайт, на котором пользователи будут публиковать рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Сервис «Список покупок» позволит пользователям создавать список продуктов, которые нужно купить для приготовления выбранных блюд. 

## Ресурсы API **«Продуктовый помощник»**:
Доступ к API осуществляется через ресурс **/api/**
- Ресурс **auth** - доступ получению и изменению токена аутентификации
- Ресурс **tags** - доступ к списку тэгов или конкретному тэгу
- Ресурс **users** - доступ к списку пользователей, регистрации пользователя, профилю пользователя, текущему пользователю, изменению пароля
- Ресурс **ingredients** - доступ к списку ингредиентов или конкретному ингредиенту
### Внутри ресурса **users**:
- Ресурс **subscriptions** - доступ к списку подписок
- Ресурс **subscribe** - осуществление подписки на пользователя или отписки от него
- Ресурс **recipes** - доступ к списку рецептов, конкретному рецепту, созданию рецепта, обновлению рецепта, удалению рецепта
### Внутри ресурса **recipes**:
- Ресурс **shopping_cart** - добавление или удаление корзины покупок
- Ресурс **download_shopping_cart** - скачивание ингредиентов из списка покупок
- Ресурс **favorite** - добавление рецепта в избранное или удаление из избранного

## Инструкции по установке:

***Клонируйте репозиторий***\
`git@github.com:epsilonm/foodgram-project-react.git`

***Перейдите в директорию foodgram-project-react/infra***\
` cd foodgram-project-react/infra`

***Создайте файл .env и укажите в нем следующие параметры:***\
```SECRET_KEY = '98770981242'
DEBUG = False
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
```

***Запустите контейнеры***\
`docker-compose up -d --build`

***Примените миграции***\
`docker-compose exec backend python manage.py migrate`

***Создайте супер-пользователя***\
`docker-compose exec backend python manage.py createsuperuser`

***Соберите статику***\
`docker-compose exec backend python manage.py collectstatic --no-input`

***Наполните базу ингредиентами***\
`docker-compose exec backend python manage.py upload_json data/ingredients.json -i`

***Наполните базу тэгами***\
`docker-compose exec backend python manage.py upload_json data/tags.json -t`

***Остановить проект***\
`docker-compose down`

## Доступ к документации
После запуска контейнеров, доступ к документации осуществляется по ссылке:
`http://localhost/api/docs/redoc.html`

## Примеры запросов к API:
***Создание рецепта***
`POST` | `http://localhost/api/recipes/`

**Request**
```
{
  "ingredients": [
    {
      "id": 1123,
      "amount": 10
    }
  ],
  "tags": [
    1,
    2
  ],
  "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAgMAAABieywaAAAACVBMVEUAAAD///9fX1/S0ecCAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAACklEQVQImWNoAAAAggCByxOyYQAAAABJRU5ErkJggg==",
  "name": "string",
  "text": "string",
  "cooking_time": 1
}
```
**Response**
```
{
  "id": 0,
  "tags": [
    {
      "id": 0,
      "name": "Завтрак",
      "color": "#E26C2D",
      "slug": "breakfast"
    }
  ],
  "author": {
    "email": "user@example.com",
    "id": 0,
    "username": "string",
    "first_name": "Вася",
    "last_name": "Пупкин",
    "is_subscribed": false
  },
  "ingredients": [
    {
      "id": 0,
      "name": "Картофель отварной",
      "measurement_unit": "г",
      "amount": 1
    }
  ],
  "is_favorited": true,
  "is_in_shopping_cart": true,
  "name": "string",
  "image": "http://foodgram.example.org/media/recipes/images/image.jpeg",
  "text": "string",
  "cooking_time": 1
}
```
