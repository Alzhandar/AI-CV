class LogRouter:
    """
    Маршрутизатор для перенаправления операций с логами в базу данных MySQL.
    """
    log_app_labels = {'app_logs', 'django_admin_log'}

    def db_for_read(self, model, **hints):
        """Чтение из базы логов для моделей логов."""
        if model._meta.app_label in self.log_app_labels:
            return 'logs'
        return None

    def db_for_write(self, model, **hints):
        """Запись в базу логов для моделей логов."""
        if model._meta.app_label in self.log_app_labels:
            return 'logs'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        """
        Разрешить связи между моделями логов или между обычными моделями,
        но не между логами и обычными моделями.
        """
        if (obj1._meta.app_label in self.log_app_labels and
                obj2._meta.app_label in self.log_app_labels):
            return True
        elif (obj1._meta.app_label not in self.log_app_labels and
                obj2._meta.app_label not in self.log_app_labels):
            return True
        return False

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Миграции для моделей логов применяются только к базе логов.
        """
        if app_label in self.log_app_labels:
            return db == 'logs'
        return db == 'default'