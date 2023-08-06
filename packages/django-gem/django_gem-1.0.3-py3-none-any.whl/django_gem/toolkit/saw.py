import contextlib
import json
import typing

from django.contrib.contenttypes.models import ContentType
from django.db import IntegrityError, transaction

from django_gem.models.mixins import GemModelMixin
from django_gem.toolkit import forge, gem_settings
from django_gem.toolkit.chest import SealedChestItem


class Saw:
    @classmethod
    @transaction.atomic
    def cut_content_type(cls, content_type_id: int, field_names: list):
        gem_cutting_enabled = gem_settings.GEM_CUTTING_ENABLED

        if not gem_cutting_enabled:
            return
        try:
            content_type: ContentType = ContentType.objects.get(id=content_type_id)
        except ContentType.DoesNotExist:
            return

        model_class = content_type.model_class()
        for model_instance in model_class.objects.all():
            if isinstance(model_class, GemModelMixin):
                model_class.update_cutting_started_at([model_instance.id])
            for field_name in field_names:
                forge.cut_model_field(model_instance, field_name)
            if isinstance(model_class, GemModelMixin):
                model_class.update_cutting_completed_at([model_instance.id])

    @classmethod
    @transaction.atomic
    def cut_models(cls, sealed_chest: str):
        gem_cutting_enabled = gem_settings.GEM_CUTTING_ENABLED

        if not gem_cutting_enabled:
            return
        try:
            unsealed_chest: typing.Dict[int, typing.List[typing.Dict]] = json.loads(sealed_chest)
        except json.JSONDecodeError:
            return

        for content_type_id, chest_items in unsealed_chest.items():
            try:
                content_type: ContentType = ContentType.objects.get(id=content_type_id)
            except ContentType.DoesNotExist:
                continue

            sealed_chest_mapping: typing.Dict[str, SealedChestItem] = {
                SealedChestItem(**item).object_id: SealedChestItem(**item) for item in chest_items
            }
            chest_item_object_ids = [chest_item for chest_item in sealed_chest_mapping]

            model_class = content_type.model_class()
            if isinstance(model_class, GemModelMixin):
                model_class.update_cutting_started_at(chest_item_object_ids)

            for model_instance in model_class.objects.filter(id__in=chest_item_object_ids):
                model_instance_id = str(model_instance.id)
                if (sealed_chest_item := sealed_chest_mapping.get(str(model_instance_id))) is None:
                    continue
                with contextlib.suppress(IntegrityError):
                    # Because of the distributed nature of cutting, the update to gem can happen
                    # after the referencing model was deleted. This will ensure we don't stop
                    # all the cuttings if something goes wrong.
                    forge.cut_model_fields(
                        model_instance,
                        sealed_chest_item.gem_fields,
                    )

            if isinstance(model_class, GemModelMixin):
                model_class.update_cutting_completed_at(chest_item_object_ids)

    @classmethod
    @transaction.atomic
    def cut_queryset(cls, content_type_id: int, object_ids: list):
        gem_cutting_enabled = gem_settings.GEM_CUTTING_ENABLED

        if not gem_cutting_enabled:
            return
        from django_gem.toolkit import forge, smith

        try:
            content_type: ContentType = ContentType.objects.get(id=content_type_id)
        except ContentType.DoesNotExist:
            return

        model_class = content_type.model_class()

        for model_instance in model_class.objects.filter(id__in=object_ids):
            reverse_cutter_model = forge.cutter_registry.get_reverse_cutter_for_model(
                model_instance
            )
            if not reverse_cutter_model or not reverse_cutter_model.model:
                continue

            for reverse_cutter_trigger in reverse_cutter_model.triggers:
                object_ids = list(reverse_cutter_trigger.callback(model_instance))
                if not object_ids:
                    continue
                reversed_cutter_model_content_type = ContentType.objects.get_for_model(
                    reverse_cutter_trigger.model
                )
                smith.add_item(
                    content_type_id=reversed_cutter_model_content_type.id,
                    object_ids=object_ids,
                    gem_fields=reverse_cutter_trigger.gem_fields,
                )
            smith.initiate_cutting()
