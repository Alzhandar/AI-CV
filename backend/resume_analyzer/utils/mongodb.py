import os
import uuid
import logging
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

logger = logging.getLogger(__name__)

# Глобальный клиент MongoDB
_mongo_client = None

def get_mongodb_client():
    """
    Получить подключение к MongoDB.
    Использует имя сервиса Docker (ai_cv_mongodb) вместо localhost.
    """
    global _mongo_client
    
    if _mongo_client is not None:
        return _mongo_client
        
    # Используем переменную окружения или имя сервиса Docker
    mongo_host = os.environ.get('MONGODB_HOST', 'ai_cv_mongodb')
    mongo_port = int(os.environ.get('MONGODB_PORT', 27017))
    mongo_user = os.environ.get('MONGODB_USERNAME', '')
    mongo_pass = os.environ.get('MONGODB_PASSWORD', '')
    
    connection_string = f"mongodb://{mongo_host}:{mongo_port}/"
    
    # Добавляем авторизацию, если учетные данные предоставлены
    if mongo_user and mongo_pass:
        connection_string = f"mongodb://{mongo_user}:{mongo_pass}@{mongo_host}:{mongo_port}/"
    
    logger.info(f"Подключение к MongoDB: {mongo_host}:{mongo_port}")
    
    try:
        client = MongoClient(connection_string, serverSelectionTimeoutMS=5000)
        # Проверяем соединение
        client.admin.command('ping')
        logger.info("Успешное подключение к MongoDB")
        _mongo_client = client
        return client
    except ConnectionFailure as e:
        logger.error(f"Ошибка подключения к MongoDB: {e}")
        # В случае ошибки возвращаем None и позволяем вызывающему коду обработать ошибку
        raise ConnectionError(f"Не удалось подключиться к MongoDB: {str(e)}")

def get_mongodb_db():
    """
    Получить базу данных MongoDB.
    """
    db_name = os.environ.get('MONGODB_DATABASE', 'resume_analyzer')
    
    try:
        client = get_mongodb_client()
        return client[db_name]
    except ConnectionError as e:
        logger.error(f"Ошибка при получении базы данных MongoDB: {e}")
        return None

def generate_mongodb_id():
    """
    Генерирует фиктивный ID в формате UUID, если MongoDB недоступна.
    """
    return str(uuid.uuid4())