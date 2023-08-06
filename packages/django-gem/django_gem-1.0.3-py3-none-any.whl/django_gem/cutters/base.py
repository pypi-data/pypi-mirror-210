class BaseCutterMetaclass(type):
    def __init__(cls, name, bases, attrs):
        super().__init__(name, bases, attrs)
        for attr_name, attr_value in attrs.items():
            side_effects = (
                getattr(attr_value, "side_effects", None)
                # Supporting Django cached_property here
                or getattr(getattr(attr_value, "real_func", None), "side_effects", None)
                # Supporting functools cached_property here
                or getattr(getattr(attr_value, "func", None), "side_effects", None)
                # Supporting regular property here
                or getattr(getattr(attr_value, "fget", None), "side_effects", None)
            )
            if side_effects is not None:
                cls.side_effects = [
                    *getattr(cls, "side_effects", []),
                    *side_effects,
                ]


class BaseCutter(metaclass=BaseCutterMetaclass):
    side_effects = []

    def __init__(self, instance):
        self.instance = instance
