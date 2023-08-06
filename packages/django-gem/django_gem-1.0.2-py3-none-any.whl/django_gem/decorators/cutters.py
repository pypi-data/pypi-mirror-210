import typing

from django.db import models
from django.db.models import Manager
from django.db.models.fields.related_descriptors import ManyToManyDescriptor

from django_gem.constants import CallbackType
from django_gem.models.base import CutterSideEffect
from django_gem.toolkit import gem_settings


def side_effects(
    *args: typing.Tuple[
        typing.Union[typing.Type[typing.Union[models.Model, ManyToManyDescriptor]], Manager],
        typing.List[str],
        CallbackType,
    ],
):
    def wrapped_function(function):
        if gem_settings.CUTTER_PROPERTY_PREFIX not in function.__name__:
            return function

        cutter_field_name = function.__name__.replace(gem_settings.CUTTER_PROPERTY_PREFIX, "")
        function.side_effects = [
            CutterSideEffect(
                model=model_class,
                callback=callback,
                affected_fields=affected_fields,
                gem_fields=[cutter_field_name],
            )
            for (model_class, affected_fields, callback) in args
        ]
        return function

    return wrapped_function
