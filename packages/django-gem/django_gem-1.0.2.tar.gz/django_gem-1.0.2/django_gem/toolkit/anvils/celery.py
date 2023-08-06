import json

from django_gem.tasks.cut_models import cut_models_task
from django_gem.toolkit.anvils.base import BaseAnvil


class CeleryAnvil(BaseAnvil):
    @classmethod
    def cut(cls, sealed_chest):
        cut_models_task.delay(sealed_chest=json.dumps(sealed_chest))
