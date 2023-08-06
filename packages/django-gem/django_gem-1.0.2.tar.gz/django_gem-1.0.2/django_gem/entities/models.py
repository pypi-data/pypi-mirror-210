import typing
from dataclasses import dataclass, field

from django.db import models

from django_gem.constants import CallbackType


@dataclass
class CutterSideEffect:
    model: typing.Type[models.Model]
    callback: CallbackType
    affected_fields: typing.List[str] = field(default_factory=lambda: [])
    gem_fields: typing.List[str] = field(default_factory=lambda: [])

    @property
    def callback_group(self) -> str:
        return self.callback.__name__


@dataclass
class CutterRelatedGemSideEffect:
    related_gem_model: typing.Type[models.Model]
    callback: CallbackType
    self_affected_fields: typing.List[str] = field(default_factory=lambda: [])
    gem_fields: typing.List[str] = field(default_factory=lambda: [])
