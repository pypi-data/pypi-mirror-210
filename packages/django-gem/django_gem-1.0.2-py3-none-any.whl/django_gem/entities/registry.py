import typing
from dataclasses import dataclass, field

from django.db import models

from django_gem.constants import CallbackType
from django_gem.cutters.base import BaseCutter
from django_gem.models.base import CutterEngineBaseModel, CutterSideEffect

# region Configuration

# region Regular cutter entities


@dataclass
class CutterModelTrigger:
    cutter: typing.Type[BaseCutter]
    gem_class: typing.Type[CutterEngineBaseModel]
    propagate_triggers: typing.Dict[str, typing.List] = field(default_factory=lambda: {})


@dataclass
class CutterModel:
    model: typing.Type[models.Model] = None
    triggers: typing.List[CutterModelTrigger] = field(default_factory=lambda: [])


# endregion

# region Reverse cutter entities


@dataclass
class ReverseCutterModel:
    model: typing.Type[models.Model] = None
    triggers: typing.List[CutterSideEffect] = field(default_factory=lambda: [])


# endregion

# endregion


# region Batches
@dataclass
class CutterBatchItem:
    model: typing.Type[models.Model]
    callback: CallbackType
    gem_fields: typing.List[str]
    affected_fields: typing.List[str] = field(default_factory=lambda: [])
    object_ids: typing.List[str] = field(default_factory=lambda: [])

    def load_object_ids(self, instance):
        try:
            self.object_ids = list(self.callback(instance))
        except Exception:  # noqa
            ...


# endregion


# region Eager Gem Recalculations
@dataclass
class EagerGemItem:
    cutter: typing.Type[BaseCutter]
    related_gem_field_name: str


# endregion
