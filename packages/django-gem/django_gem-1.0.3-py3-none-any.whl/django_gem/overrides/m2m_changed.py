import typing

from django.db import transaction

from django_gem.entities.registry import CutterBatchItem
from django_gem.overrides.utils import add_cut_items

CUTTER_M2M_SIGNAL_ACTIONS = ["pre_add", "pre_remove", "pre_clear"]


def m2m_changed_hook(
    cut_batch_items: typing.List[CutterBatchItem],
):
    def m2m_changed(sender, instance, action, **kwargs):  # noqa
        from django_gem.toolkit import gem_settings, smith

        gem_cutting_enabled = gem_settings.GEM_CUTTING_ENABLED

        if action not in CUTTER_M2M_SIGNAL_ACTIONS:
            return

        with transaction.atomic():
            changed_cut_batch_items = []
            for cut_batch_item in cut_batch_items:
                cut_batch_item.load_object_ids(instance)
                changed_cut_batch_items.append(cut_batch_item)

            if not gem_cutting_enabled:
                return

            add_cut_items(smith, changed_cut_batch_items)

            transaction.on_commit(
                lambda: smith.initiate_cutting(),
            )

    return m2m_changed
