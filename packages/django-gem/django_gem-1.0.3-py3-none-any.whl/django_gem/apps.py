from django.apps import AppConfig


class DjangoGemsConfig(AppConfig):
    name = "django_gem"

    def ready(self):
        from django_gem.toolkit import cutter_registry, smith

        cutter_registry.ready()
        smith.load()
        super().ready()
