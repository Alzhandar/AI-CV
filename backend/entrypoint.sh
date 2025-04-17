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

echo "Проверка наличия суперпользователя..."
python -c "
import os
from django.contrib.auth import get_user_model;
User = get_user_model();
if not User.objects.filter(email='${DJANGO_ADMIN_EMAIL:-admin@example.com}').exists():
    User.objects.create_superuser('${DJANGO_ADMIN_EMAIL:-admin@example.com}', '${DJANGO_ADMIN_PASSWORD:-admin}')
    print('Суперпользователь создан.');
else:
    print('Суперпользователь уже существует.');
"
exec "$@"