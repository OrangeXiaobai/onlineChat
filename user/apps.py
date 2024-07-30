from django.apps import AppConfig


class UserConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'user'

    # 通过覆盖 ready 方法，在应用启动时调用，导入 login.signals 模块，以确保信号处理器在应用初始化时被加载。
    def ready(self):
        import user.signals