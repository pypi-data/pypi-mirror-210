import typing
from collections import defaultdict
from dataclasses import asdict, dataclass

from django.contrib.contenttypes.models import ContentType

from django_gem.models.mixins import GemModelMixin


@dataclass
class ChestItem:
    gem_fields: list
    object_ids: list


@dataclass
class SealedChestItem:
    object_id: str
    gem_fields: list


class Chest:
    """Storage for all pending cuttings"""

    cut_models: typing.Dict[int, typing.List[ChestItem]] = defaultdict(list)

    @classmethod
    def seal_items(cls, chest_items: typing.List[ChestItem]) -> typing.List[SealedChestItem]:
        sealed_item_mapping: typing.Dict[str, SealedChestItem] = {}
        for chest_item in chest_items:
            for object_id in chest_item.object_ids:
                if sealed_item_mapping.get(object_id):
                    sealed_item_mapping[object_id].gem_fields = list(
                        {*sealed_item_mapping[object_id].gem_fields, *chest_item.gem_fields}
                    )
                else:
                    sealed_item_mapping[object_id] = SealedChestItem(
                        object_id=object_id,
                        gem_fields=chest_item.gem_fields,
                    )
        return list(sealed_item_mapping.values())

    def add(self, content_type_id: int, object_ids: list, gem_fields: list):
        object_ids = [object_id for object_id in object_ids if object_id is not None]
        if not object_ids:
            return

        self.cut_models[content_type_id].append(
            ChestItem(
                gem_fields=gem_fields,
                object_ids=[str(object_id) for object_id in object_ids if object_id is not None],
            )
        )

    def reset(self):
        self.cut_models = defaultdict(list)

    def is_empty(self):
        return not bool(self.cut_models)

    def get_sealed_chest(self, update_cutting_started_at=True):
        sealed_chest = {}

        for content_type_id, chest_items in self.cut_models.items():
            try:
                content_type = ContentType.objects.get(id=content_type_id)
            except ContentType.DoesNotExist:
                continue

            if update_cutting_started_at:
                content_type_model = content_type.model_class()
                if isinstance(content_type_model, GemModelMixin):
                    content_type_model.update_cutting_started_at(
                        [object_id for item in chest_items for object_id in item.object_ids]
                    )

            sealed_chest[content_type_id] = [
                asdict(item) for item in self.seal_items(chest_items=chest_items)
            ]
        return sealed_chest
