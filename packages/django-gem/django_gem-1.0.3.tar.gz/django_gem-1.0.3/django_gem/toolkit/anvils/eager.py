import json

from django_gem.toolkit.anvils.base import BaseAnvil


class EagerAnvil(BaseAnvil):
    @classmethod
    def cut(cls, sealed_chest):
        from django_gem.toolkit.saw import Saw

        Saw.cut_models(sealed_chest=json.dumps(sealed_chest))
