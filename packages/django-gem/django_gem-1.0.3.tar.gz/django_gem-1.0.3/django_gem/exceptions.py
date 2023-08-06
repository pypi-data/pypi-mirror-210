import typing

from django.db import models

from django_gem.cutters.base import BaseCutter


class CutterFieldMissingException(Exception):
    def __init__(self, model_class: typing.Type[models.Model], field_name: str):
        self.model_class_name = model_class.__name__
        self.field_name = field_name

    def __str__(self):
        return f'Can not find field "{self.field_name}" for model {self.model_class_name}'


class UnusedCutterMethodException(Exception):
    def __init__(self, cutter_class: typing.Type[BaseCutter], field_name: str):
        self.cutter_class_name = cutter_class.__name__
        self.field_name = field_name

    def __str__(self):
        return f'Unused cutter method "{self.field_name}" for cutter {self.cutter_class_name}'


class CutterClassFieldMissingException(Exception):
    def __init__(self, cutter_class: typing.Type[BaseCutter], field_name: str):
        self.cutter_class_name = cutter_class.__name__
        self.field_name = field_name

    def __str__(self):
        return f'Can not find method "{self.field_name}" for cutter {self.cutter_class_name}'
