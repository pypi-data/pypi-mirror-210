import typing

from django.db import models
from django.db.models.base import ModelBase

from django_gem.entities.models import CutterRelatedGemSideEffect, CutterSideEffect
from django_gem.toolkit.settings import gem_settings


class CutterEngineMetaBase:
    model = None
    related_name = None
    cutter = None
    self_affected_fields: typing.List[str] = []
    propagate_triggers: typing.Dict[str, typing.List] = {}
    side_effects: typing.List[CutterSideEffect] = []
    related_gem_side_effects: typing.List[CutterRelatedGemSideEffect] = []


class CutterEngineBase(ModelBase):
    def __new__(cls, name, bases, attrs):
        if cutter_engine_meta := attrs.get("CutterEngineMeta"):
            if cutter_engine_meta and cutter_engine_meta.model:
                related_name = (
                    getattr(cutter_engine_meta, "related_name", None)
                    or gem_settings.DEFAULT_RELATED_GEM_FIELD_NAME
                )
                attrs[gem_settings.CUTTER_MODEL_RELATED_NAME] = models.OneToOneField(
                    cutter_engine_meta.model,
                    on_delete=models.CASCADE,
                    null=True,
                    related_name=related_name,
                )
        klass = super().__new__(cls, name, bases, attrs)
        return klass


class CutterEngineBaseModel(models.Model, metaclass=CutterEngineBase):
    BASE_FIELDS = ["id", gem_settings.CUTTER_MODEL_RELATED_NAME]

    def __str__(self):
        return f"Gem of {self.__getattribute__(gem_settings.CUTTER_MODEL_RELATED_NAME)}"

    class Meta:
        abstract = True

    @classmethod
    def get_gem_fields(cls):
        ignored_fields = cls.BASE_FIELDS
        if gem_ignored_fields := gem_settings.GEM_IGNORED_FIELDS:
            ignored_fields = [*cls.BASE_FIELDS, *gem_ignored_fields]
        return [field.name for field in cls._meta.fields if field.name not in ignored_fields]

    class CutterEngineMeta(CutterEngineMetaBase):
        ...
