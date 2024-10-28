from django.apps import AppConfig

class UsersConfig(AppConfig):
    name = 'users'

    def ready(self):
        import users.signals  # Import signals to register them
