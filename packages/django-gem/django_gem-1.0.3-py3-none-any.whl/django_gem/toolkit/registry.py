import typing
from collections import defaultdict

from django.db.models.fields.related_descriptors import ManyToManyDescriptor
from django.db.models.signals import m2m_changed
from django.utils.module_loading import autodiscover_modules

from django_gem.entities.registry import (
    CutterBatchItem,
    CutterModel,
    CutterModelTrigger,
    EagerGemItem,
    ReverseCutterModel,
)
from django_gem.models.base import CutterEngineBaseModel, CutterSideEffect
from django_gem.overrides import (
    delete_cutting_hook,
    m2m_changed_hook,
    save_cutting_hook,
)
from django_gem.toolkit import gem_settings
from django_gem.validators import CutterEngineValidator


class CutterRegistry:
    """Collects models dependencies to build cutter classes dependencies map"""

    # Direct cutters contains the mapping of which model needs to be updated and how
    direct_cutters = defaultdict(CutterModel)
    # Reverse cutters contains the related models mapping that should trigger updates
    reverse_cutters = defaultdict(ReverseCutterModel)

    @classmethod
    def get_model_key(cls, model_class):
        if isinstance(model_class, ManyToManyDescriptor):
            return f"{model_class.through._meta.app_label}.{model_class.through._meta.model_name}"  # noqa
        return f"{model_class._meta.app_label}.{model_class._meta.model_name}"  # noqa

    def get_cutter_for_model(self, model_class):
        autodiscover_modules("apps")
        return self.direct_cutters.get(self.get_model_key(model_class))

    def get_reverse_cutter_for_model(self, model_class):
        autodiscover_modules("apps")
        return self.reverse_cutters.get(self.get_model_key(model_class))

    def get_model_eager_gem_item(self, model_instance, field_name) -> typing.Optional[EagerGemItem]:
        cutter_model = self.get_cutter_for_model(model_instance)
        if not cutter_model or not cutter_model.model:
            return None
        for registered_cutter in cutter_model.triggers:
            gem_class = registered_cutter.gem_class
            if field_name not in [field.name for field in gem_class._meta.fields]:
                continue
            related_gem_field_name = (
                getattr(gem_class.CutterEngineMeta, "related_name", None)
                or gem_settings.DEFAULT_RELATED_GEM_FIELD_NAME
            )
            return EagerGemItem(
                related_gem_field_name=related_gem_field_name,
                cutter=registered_cutter.cutter,
            )
        return None

    def get_eager_field_value(self, model_instance, field_name, default_value=None):
        eager_gem_item = self.get_model_eager_gem_item(
            model_instance=model_instance,
            field_name=field_name,
        )
        if not eager_gem_item:
            return default_value
        cached_cutter_field_name = (
            f"__{eager_gem_item.related_gem_field_name}_{gem_settings.CACHED_GEM_CUTTER_FIELD_NAME}"
        )
        cutter = getattr(model_instance, cached_cutter_field_name, None)
        if not cutter:
            cutter = eager_gem_item.cutter(model_instance)
            setattr(model_instance, cached_cutter_field_name, cutter)
        if hasattr(cutter, f"{gem_settings.CUTTER_PROPERTY_PREFIX}{field_name}"):
            return getattr(cutter, f"{gem_settings.CUTTER_PROPERTY_PREFIX}{field_name}")
        return default_value

    def register_cutter(self, gem_class: typing.Type[CutterEngineBaseModel]):
        model_key = self.get_model_key(gem_class.CutterEngineMeta.model)
        gem_class.CutterEngineMeta.side_effects = [
            *gem_class.CutterEngineMeta.side_effects,
            *gem_class.CutterEngineMeta.cutter.side_effects,
        ]
        CutterEngineValidator(gem_class).validate()
        self.direct_cutters[model_key].model = gem_class.CutterEngineMeta.model
        self.direct_cutters[model_key].triggers.append(
            CutterModelTrigger(
                cutter=gem_class.CutterEngineMeta.cutter,
                gem_class=gem_class,
                propagate_triggers=gem_class.CutterEngineMeta.propagate_triggers,
            )
        )
        for side_effect in gem_class.CutterEngineMeta.side_effects:
            self._add_side_effect_to_triggers(gem_class, side_effect)

    def _add_side_effect_to_triggers(
        self,
        gem_class: typing.Type[CutterEngineBaseModel],
        side_effect: CutterSideEffect,
    ):
        side_effect_model = side_effect.model
        side_effect_model_key = self.get_model_key(side_effect_model)
        gem_fields = getattr(side_effect, "gem_fields", None) or gem_class.get_gem_fields()
        side_effect_affected_fields = getattr(side_effect, "affected_fields", None)
        for trigger in self.reverse_cutters[side_effect_model_key].triggers:
            if (
                trigger.callback_group == side_effect.callback_group
                and (trigger.model == gem_class.CutterEngineMeta.model)
                and (trigger.affected_fields == side_effect_affected_fields)
            ):
                trigger.gem_fields = [
                    *trigger.gem_fields,
                    *gem_fields,
                ]
                return
        self.reverse_cutters[side_effect_model_key].model = side_effect_model
        self.reverse_cutters[side_effect_model_key].triggers.append(
            CutterSideEffect(
                model=gem_class.CutterEngineMeta.model,
                callback=side_effect.callback,
                gem_fields=gem_fields,
                affected_fields=side_effect_affected_fields,
            )
        )

    def load(self):
        autodiscover_modules("gems")
        for subclass in self.get_subclasses(CutterEngineBaseModel):
            self.register_cutter(subclass)

    def get_subclasses(
        self, parent_class: typing.Type[CutterEngineBaseModel]
    ) -> typing.List[typing.Type[CutterEngineBaseModel]]:
        subclasses: typing.List[typing.Type[CutterEngineBaseModel]] = []
        for subclass in parent_class.__subclasses__():
            if len(subclass.__subclasses__()) > 0:
                subclasses.extend(self.get_subclasses(subclass))
            else:
                subclasses.append(subclass)
        return subclasses

    def ready(self):
        self.load()
        for app, triggered_model in self.reverse_cutters.items():
            cut_batch_items = [
                CutterBatchItem(
                    model=item.model,
                    gem_fields=item.gem_fields,
                    affected_fields=item.affected_fields,
                    callback=item.callback,
                )
                for item in triggered_model.triggers
            ]
            if isinstance(triggered_model.model, ManyToManyDescriptor):
                m2m_changed.connect(
                    m2m_changed_hook(cut_batch_items),
                    sender=triggered_model.model.through,  # noqa
                )
            else:
                triggered_model.model.save = save_cutting_hook(
                    triggered_model.model.save,
                    cut_batch_items,
                )
                triggered_model.model.delete = delete_cutting_hook(
                    triggered_model.model.delete,
                    cut_batch_items,
                )


cutter_registry = CutterRegistry()
