import logging
from typing import Optional, Any

from django.conf import settings
from pymongo import MongoClient

logger = logging.getLogger(__name__)

_mongo_client: Optional[MongoClient] = None
_mongo_db = None


def get_mongodb_client() -> MongoClient:
    global _mongo_client
    
    if _mongo_client is not None:
        return _mongo_client
    
    mongo_uri = getattr(settings, 'MONGO_URI', None)
    mongo_host = getattr(settings, 'MONGO_HOST', 'localhost')
    mongo_port = getattr(settings, 'MONGO_PORT', 27017)
    mongo_user = getattr(settings, 'MONGO_USER', None)
    mongo_password = getattr(settings, 'MONGO_PASSWORD', None)
    
    try:
        if mongo_uri:
            _mongo_client = MongoClient(mongo_uri)
            logger.info("Подключение к MongoDB успешно установлено через URI")
        else:
            connection_args = {
                'host': mongo_host,
                'port': mongo_port
            }
            
            if mongo_user and mongo_password:
                connection_args['username'] = mongo_user
                connection_args['password'] = mongo_password
            
            _mongo_client = MongoClient(**connection_args)
            logger.info(f"Подключение к MongoDB успешно установлено на {mongo_host}:{mongo_port}")
        
        _mongo_client.admin.command('ping')
        
        return _mongo_client
        
    except Exception as e:
        logger.error(f"Ошибка подключения к MongoDB: {str(e)}")
        raise ConnectionError(f"Не удалось подключиться к MongoDB: {str(e)}")


def get_mongodb_db(db_name: Optional[str] = None) -> Any:
    global _mongo_db
    
    if _mongo_db is not None and db_name is None:
        return _mongo_db
    
    db_name = db_name or getattr(settings, 'MONGO_DB_NAME', 'resume_analyzer')
    client = get_mongodb_client()
    _mongo_db = client[db_name]
    
    return _mongo_db


def close_mongodb_connection() -> None:
    global _mongo_client, _mongo_db
    
    if _mongo_client is not None:
        try:
            _mongo_client.close()
            logger.info("Соединение с MongoDB закрыто")
        except Exception as e:
            logger.error(f"Ошибка при закрытии соединения с MongoDB: {str(e)}")
        finally:
            _mongo_client = None
            _mongo_db = None