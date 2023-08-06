import typing

from django.contrib.contenttypes.models import ContentType

from django_gem.entities.registry import CutterBatchItem
from django_gem.models.mixins import GemTriggerMixin


def is_cutting_needed(model_instance, affected_fields):
    return (
        model_instance._state.adding  # noqa
        or not affected_fields
        or not isinstance(model_instance, GemTriggerMixin)
        or model_instance.is_any_field_changed(affected_fields)
    )


def add_cut_items(
    smith,
    cut_batch_items: typing.List[CutterBatchItem],
):
    # Marking cut as started outside the transaction to avoid locks
    for cut_batch_item in cut_batch_items:
        if not cut_batch_item.object_ids:
            continue

        smith.add_item(
            content_type_id=ContentType.objects.get_for_model(cut_batch_item.model).id,
            object_ids=list(set(cut_batch_item.object_ids)),
            gem_fields=list(set(cut_batch_item.gem_fields)),
        )
