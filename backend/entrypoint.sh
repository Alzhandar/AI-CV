#!/bin/bash

set -e

until nc -z $POSTGRES_HOST 5432; do
  echo "Ожидание запуска PostgreSQL..."
  sleep 2
done

until nc -z $MYSQL_HOST 3306; do 
  echo "Ожидание запуска MySQL..."
  sleep 2
done

until nc -z $MONGO_HOST 27017; do
  echo "Ожидание запуска MongoDB..."
  sleep 2
done

echo "Применение миграций для PostgreSQL..."
python manage.py migrate

echo "Применение миграций для MySQL (логи)..."
python manage.py migrate --database=logs

echo "Сбор статических файлов..."
python manage.py collectstatic --noinput

exec "$@"