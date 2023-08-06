from django.conf import settings


class DjangoGemsSettings:
    # region Non-configurable fields
    DEFAULT_RELATED_GEM_FIELD_NAME = "gem"
    CACHED_GEM_CUTTER_FIELD_NAME = "cached_cutter"
    # endregion

    CUTTER_PROPERTY_PREFIX = "cut_"
    CUTTER_MODEL_RELATED_NAME = "cutter_target"
    CUTTER_PROPAGATED_TRIGGERS_MAX_DEPTH = 10
    GEM_IGNORED_FIELDS = []
    GEM_CUTTING_ENABLED = True
    GEM_ANVILS = []

    def __init__(self):
        self.load()

    def load(self):
        if hasattr(settings, "CUTTER_PROPERTY_PREFIX"):
            self.CUTTER_PROPERTY_PREFIX = settings.CUTTER_PROPERTY_PREFIX
        if hasattr(settings, "CUTTER_PROPAGATED_TRIGGERS_MAX_DEPTH"):
            self.CUTTER_PROPAGATED_TRIGGERS_MAX_DEPTH = (
                settings.CUTTER_PROPAGATED_TRIGGERS_MAX_DEPTH
            )
        if hasattr(settings, "CUTTER_MODEL_RELATED_NAME"):
            self.CUTTER_MODEL_RELATED_NAME = settings.CUTTER_MODEL_RELATED_NAME
        if hasattr(settings, "GEM_IGNORED_FIELDS"):
            self.GEM_IGNORED_FIELDS = settings.GEM_IGNORED_FIELDS
        if hasattr(settings, "GEM_CUTTING_ENABLED"):
            self.GEM_CUTTING_ENABLED = settings.GEM_CUTTING_ENABLED
        if hasattr(settings, "GEM_ANVILS"):
            self.GEM_ANVILS = settings.GEM_ANVILS


gem_settings = DjangoGemsSettings()
