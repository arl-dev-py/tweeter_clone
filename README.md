# TweeterClone API

Корпоративный Twitter-клон.

## Запуск (1 команда)

git clone https://github.com/arl-dev-py/TweeterClone.git
cd TweeterClone
mkdir -p media
docker-compose up -d --build

Swagger: http://localhost:8000/docs  
БД: localhost:5432 (user/password)

## Демо (api-key: test-api-key)

# 1. Создать суперюзера
curl -X POST http://localhost:8000/api/users/superuser \
  -H "Content-Type: application/json" \
  -d '{"username": "admin"}'

# 2. Создать твит
curl -X POST http://localhost:8000/api/tweets \
  -H "api-key: test-api-key" \
  -H "Content-Type: application/json" \
  -d '{"tweet_data": "Привет из микроблога!", "tweet_media_ids": []}'

## API эндпоинты

POST    /api/tweets                    Новый твит {tweet_data, tweet_media_ids[]}
POST    /api/medias                    Загрузить картинку (form file)
DELETE  /api/tweets/{id}               Удалить свой твит
POST    /api/tweets/{id}/likes         Поставить лайк
DELETE  /api/tweets/{id}/likes         Убрать лайк
POST    /api/users/{id}/follow         Подписаться
DELETE  /api/users/{id}/follow         Отписаться
GET     /api/tweets                    Лента (following, сортировка по популярности)
GET     /api/users/me                  Мой профиль {followers, following}
GET     /api/users/{id}                Профиль пользователя

Авторизация: Header `api-key: test-api-key`

## Команды разработки

# Логи
docker-compose logs -f api

# Очистка
docker-compose down -v

# Тесты
pytest tests/ --cov=app/routers --cov-report=term
