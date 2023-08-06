import typing

from django.db import transaction

from django_gem.entities.registry import CutterBatchItem
from django_gem.models.mixins import GemCutConditionalMixin
from django_gem.overrides.utils import add_cut_items, is_cutting_needed


def save_cutting_hook(
    save_func,
    cut_batch_items: typing.List[CutterBatchItem],
):
    def wrapped_trigger(self, *args, **kwargs):
        from django_gem.toolkit import gem_settings, smith

        gem_cutting_enabled = gem_settings.GEM_CUTTING_ENABLED

        should_cut = True
        if isinstance(self, GemCutConditionalMixin):
            should_cut = self.should_cut_on_save(*args, **kwargs)

        with transaction.atomic():
            prepared_cut_batch_items = []
            changed_cut_batch_items = []
            if should_cut:
                prepared_cut_batch_items = [
                    cut_batch_item
                    for cut_batch_item in cut_batch_items
                    if is_cutting_needed(self, cut_batch_item.affected_fields)
                ]

            save_func(self, *args, **kwargs)
            if not gem_cutting_enabled or not should_cut:
                return

            for cut_batch_item in prepared_cut_batch_items:
                cut_batch_item.load_object_ids(self)
                changed_cut_batch_items.append(cut_batch_item)

            add_cut_items(smith, changed_cut_batch_items)

            transaction.on_commit(
                lambda: smith.initiate_cutting(),
            )

    return wrapped_trigger
