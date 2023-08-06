import typing

from django.utils.translation import gettext_lazy as _

CallbackType = typing.NewType(
    "CallbackType",
    typing.Callable[[typing.Any], typing.Union[typing.List, typing.Set]],
)


class GemLogEntryAction:
    CREATE = 0
    UPDATE = 1
    DELETE = 2

    @classmethod
    def to_choices(cls):
        return (
            (cls.CREATE, _("create")),
            (cls.UPDATE, _("update")),
            (cls.DELETE, _("delete")),
        )
