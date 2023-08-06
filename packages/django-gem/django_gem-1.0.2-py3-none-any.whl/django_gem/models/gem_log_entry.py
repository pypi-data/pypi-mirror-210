import uuid

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from django_gem.constants import GemLogEntryAction
from django_gem.models.managers.gem_log_entry_manager import GemLogEntryManager


class GemLogEntry(models.Model):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, serialize=False, editable=False, unique=True
    )
    content_type = models.ForeignKey(
        to="contenttypes.ContentType",
        on_delete=models.CASCADE,
        related_name="+",
        verbose_name=_("content type"),
    )
    object_id = models.CharField(db_index=True, max_length=255, verbose_name=_("object id"))
    action = models.PositiveSmallIntegerField(
        choices=GemLogEntryAction.to_choices(), verbose_name=_("action"), db_index=True
    )
    actor = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="+",
        verbose_name=_("actor"),
    )
    changes = models.JSONField(verbose_name=_("Model changed fields"))
    timestamp = models.DateTimeField(db_index=True, auto_now_add=True, verbose_name=_("timestamp"))

    objects = GemLogEntryManager()

    class Meta:
        get_latest_by = "timestamp"
        ordering = ["-timestamp"]
        verbose_name = _("gem log entry")
        verbose_name_plural = _("gem log entries")
