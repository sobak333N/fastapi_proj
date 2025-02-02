# PET-project. Backend

Данный проект является API для онлайн системы курсов, backend-часть приложения.

## Предварительные требования

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

## Установка и запуск

### 1. Создание файла окружения

Скопируйте содержимое файла `.env.example` в новый файл с названием `.env`.

Для этого можно выполнить в терминале команду:

```bash
cp .env.example .env
```

### 2. Запуск контейнеров

Запустите проект с помощью Docker Compose:

```bash
docker compose up
```

Дождитесь успешного запуска всех контейнеров.

### 3. Доступ к API

После успешного запуска перейдите по ссылке:

[http://localhost/api/docs](http://localhost/api/v1/docs)

Здесь вы сможете ознакомиться с документацией API через Swagger 
