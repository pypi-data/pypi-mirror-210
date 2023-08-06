import importlib
import typing

from django_gem.logger import logger
from django_gem.toolkit import gem_settings
from django_gem.toolkit.anvils.base import BaseAnvil
from django_gem.toolkit.chest import Chest


class Smith:
    """Handles data collection and initiates cut process"""

    chest = Chest()
    anvils: typing.List[BaseAnvil] = []

    def add_item(self, content_type_id: int, object_ids: list, gem_fields: list):
        self.chest.add(content_type_id, object_ids, gem_fields)

    def add_anvil(self, anvil: BaseAnvil):
        self.anvils.append(anvil)

    def load(self):
        for anvil_import in gem_settings.GEM_ANVILS:
            try:
                anvil_module, anvil_class = anvil_import.rsplit(".", 1)
            except ValueError:
                logger.error("Error importing %s: Anvil import misconfigured", anvil_import)
                continue
            try:
                anvil: typing.Type[BaseAnvil] = getattr(
                    importlib.import_module(anvil_module), anvil_class
                )
            except ImportError as e:
                logger.error("Error importing %s: %s", anvil_import, e)
                continue
            if not anvil:
                logger.error("Error configuring %s: %s not found", anvil_import, anvil_class)
                continue
            self.add_anvil(anvil())

    def initiate_cutting(self):
        if self.chest.is_empty():
            return

        sealed_chest = self.chest.get_sealed_chest()
        for anvil in self.anvils:
            anvil.cut(sealed_chest)
        self.chest.reset()


smith = Smith()
