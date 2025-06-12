from django.apps import AppConfig




class UserConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'user'




class UsersConfig(AppConfig):
    name = 'users'


    def ready(self):
        import user.signals