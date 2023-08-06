from django.test import override_settings

from django_gem.toolkit import gem_settings


class override_gem_settings(override_settings):  # noqa
    def enable(self):
        super().enable()
        gem_settings.load()

    def disable(self):
        super().disable()
        gem_settings.load()
