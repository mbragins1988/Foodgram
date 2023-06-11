# Проект Foodgram
![Github actions](https://github.com/mbragins1988/yamdb_final/actions/workflows/yamdb_workflow.yml/badge.svg)

### Описание
На сервисе Foodgram пользователи смогут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.


### Как запустить проект на удаленном сервере

Запустить и подготовить удаленный сервер.
Войти на свой удаленный сервер в терминале (ssh your_login@pu.bl.ic.ip)

Остановить службу nginx

```
sudo systemctl stop nginx
```

Установить docker

```
sudo apt install docker.io
```

Установить docker-compose

```
sudo curl -L "https://github.com/docker/compose/releases/download/v2.17.3/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
```
```
sudo chmod +x /usr/local/bin/docker-compose
```

Скопировать файлы docker-compose.yaml и nginx/default.conf из вашего проекта на сервер в home/<ваш_username>/docker-compose.yaml и home/<ваш_username>/nginx/default.conf соответственно

Произвести необходимые изменения в проекте, сохранить файлы

Добавить изменения

```
git add --all
```

Сделать коммит

```
git commit -m "Commit"
```

Отправить изменения в удалённый репозиторий

```
git push
```

В Git Actions workflow выполнит:
- проверку кода на соответствие стандарту PEP8 с помощью пакета flake8
- запустит pytest
- соберет и доставит докер-образ на Docker Hub
- деплой проекта на боевой сервер
- отправит уведомление в Telegram о том, что процесс деплоя успешно завершился

В директории с файлом docker-compose.yaml

Запустите миграции
```
docker-compose exec backend python manage.py migrate
```

Импортируйте список ингредиентов в базу данных
```
docker-compose exec backend python manage.py import_date
```

Подключите статику для админ-панели
```
sudo docker-compose exec -T backend python manage.py collectstatic --no-input
```

### документация на локальном компьютере:
http://127.0.0.1:8000/redoc/

### документация на удаленном сервере:
http://158.160.46.62/api/docs/

### Стек технологий:
- Python 3.7
- Django
- Django REST framework
- Docker

## Разработчики:
- Михаил Брагин
