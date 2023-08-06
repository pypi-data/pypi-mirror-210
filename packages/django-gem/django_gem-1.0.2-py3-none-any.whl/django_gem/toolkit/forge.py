import typing

from django.utils.module_loading import autodiscover_modules

from django_gem.cutters.base import BaseCutter
from django_gem.models.base import CutterEngineBaseModel
from django_gem.toolkit import cutter_registry, gem_settings


class Forge:
    """Engine for running cut methods"""

    def __init__(self, registry):
        self.cutter_registry = registry

    def cut_model_field(self, model_instance, field_name):
        self.cut_model_fields(model_instance, [field_name])

    def cut_model_fields(self, model_instance, field_names):
        cut_fields = []
        autodiscover_modules("apps")
        cutter_model = self.cutter_registry.get_cutter_for_model(model_instance)
        if not cutter_model or not cutter_model.model:
            return None
        for registered_cutter in cutter_model.triggers:
            cutter_class, gem_class, propagate_triggers = (
                registered_cutter.cutter,
                registered_cutter.gem_class,
                registered_cutter.propagate_triggers,
            )
            cutter = cutter_class(model_instance)
            gem_instance, _ = gem_class.objects.get_or_create(
                **{gem_settings.CUTTER_MODEL_RELATED_NAME: model_instance},
            )
            for field_name in field_names:
                cutter_target_method = f"{gem_settings.CUTTER_PROPERTY_PREFIX}{field_name}"
                if not hasattr(cutter_class, cutter_target_method):
                    continue

                if field_name not in cut_fields:
                    setattr(
                        gem_instance,
                        field_name,
                        getattr(cutter, cutter_target_method, None),
                    )
                cut_fields.append(field_name)
                gem_instance = self.cut_propagated_triggers(
                    field_name,
                    propagate_triggers,
                    cutter,
                    gem_instance,
                    cut_fields,
                )
                self.cut_related_gem(gem_instance, gem_class, field_name)
            gem_instance.save()

    @classmethod
    def cut_propagated_triggers(
        cls,
        field_name: str,
        propagate_triggers,
        cutter_instance: BaseCutter,
        gem_instance,
        cut_fields: list,
        max_depth=0,
    ):
        if field_name in propagate_triggers:
            for propagated_trigger in propagate_triggers[field_name]:
                cutter_target_method = f"{gem_settings.CUTTER_PROPERTY_PREFIX}{propagated_trigger}"
                if not hasattr(cutter_instance.__class__, cutter_target_method):
                    continue

                if propagated_trigger not in cut_fields:
                    setattr(
                        gem_instance,
                        propagated_trigger,
                        getattr(cutter_instance, cutter_target_method, None),
                    )
                cut_fields.append(propagated_trigger)
                # Traversing the whole dict to find next dependencies
                if (
                    propagated_trigger != field_name
                    and max_depth < gem_settings.CUTTER_PROPAGATED_TRIGGERS_MAX_DEPTH
                ):
                    gem_instance = cls.cut_propagated_triggers(
                        propagated_trigger,
                        propagate_triggers,
                        cutter_instance,
                        gem_instance,
                        cut_fields,
                        max_depth + 1,
                    )
        return gem_instance

    def cut_related_gem(
        self,
        gem_instance,
        gem_class: typing.Type[CutterEngineBaseModel],
        field_name,
    ):
        for related_gem_side_effect in gem_class.CutterEngineMeta.related_gem_side_effects:
            query_field_name = f"{gem_settings.CUTTER_MODEL_RELATED_NAME}_id__in"
            query = {query_field_name: related_gem_side_effect.callback(gem_instance)}
            cut_related_gems = related_gem_side_effect.related_gem_model.objects.filter(**query)
            if field_name in related_gem_side_effect.self_affected_fields:
                for model_instance in cut_related_gems:
                    self.cut_model_fields(
                        model_instance.__getattribute__(gem_settings.CUTTER_MODEL_RELATED_NAME),
                        related_gem_side_effect.gem_fields,
                    )

    def cut_model(self, model_instance):
        autodiscover_modules("apps")
        cutter_model = self.cutter_registry.get_cutter_for_model(model_instance)
        if not cutter_model or not cutter_model.model:
            return None
        cut_fields = []
        for cutter in cutter_model.triggers:
            gem_class = cutter.gem_class
            if not gem_class:
                continue
            cut_fields.extend(gem_class.get_gem_fields())
        if not cut_fields:
            return None
        return self.cut_model_fields(model_instance, cut_fields)


forge = Forge(cutter_registry)
