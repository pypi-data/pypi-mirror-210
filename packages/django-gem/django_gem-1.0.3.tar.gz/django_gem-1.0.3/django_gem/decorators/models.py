import typing

from django.db import models

from django_gem.entities.context import gem_cutting_context
from django_gem.models.mixins import GemModelMixin
from django_gem.toolkit import cutter_registry


class GemProperty:  # noqa: N801
    def __init__(self, func=None, default_value=None, override_gem_field_name=None):
        self.func = func
        if self.func:
            self.name = func.__name__
        if override_gem_field_name:
            self.name = override_gem_field_name
        self.default_value = default_value

    def __call__(self, *args, **kwargs):
        if len(args) != 1:
            raise ValueError("`gem_property` is misconfigured", args, kwargs)
        self.func = args[0]
        self.name = self.func.__name__
        return self

    def __get__(
        self, instance: typing.Union[typing.Optional[GemModelMixin], models.Model], cls=None
    ):
        if not instance:
            return self.func

        should_return_eager_value = gem_cutting_context.return_eager_value
        if isinstance(instance, GemModelMixin):
            should_return_eager_value = (
                should_return_eager_value and not instance.is_cutting_in_progress
            )
        try:
            if not should_return_eager_value:
                return self.func(instance)
        except AttributeError:
            ...
        return cutter_registry.get_eager_field_value(
            instance,
            self.name,
            default_value=self.default_value,
        )


gem_property = GemProperty
