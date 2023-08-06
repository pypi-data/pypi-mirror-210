import decimal

from crum import get_current_user
from dirtyfields import DirtyFieldsMixin
from django.db import models
from django.utils import timezone

from django_gem.constants import GemLogEntryAction
from django_gem.models import GemLogEntry


class GemTriggerMixin(DirtyFieldsMixin):
    def is_any_field_changed(self, fields: list):
        if fields:
            return True
        dirty_fields = self.get_dirty_fields(check_relationship=True)
        return any(field in dirty_fields for field in fields)


class GemAuditLogMixin(DirtyFieldsMixin):
    @classmethod
    def field_value(cls, instance, field_name):
        if not instance:
            return None
        field_value = instance.__getattribute__(field_name)
        if isinstance(field_value, decimal.Decimal):
            return float(field_value)
        if isinstance(field_value, models.Model):
            return field_value.pk
        return field_value

    def save_log_entry(self, is_adding: bool, dirty_fields: dict):
        if not hasattr(self, "get_gem_fields") or not dirty_fields:
            return
        changes = {
            field_name: self.field_value(self, field_name) for field_name in self.get_gem_fields()
        }

        if changes:
            user = get_current_user()
            if user and not user.pk:
                user = None
            GemLogEntry.objects.log_create(
                self,
                action=GemLogEntryAction.CREATE if is_adding else GemLogEntryAction.UPDATE,
                changes=changes,
                actor=user,
            )

    def save(self, *args, **kwargs):
        is_adding, dirty_fields = self._state.adding, self.get_dirty_fields()  # noqa
        super().save(*args, **kwargs)  # noqa
        self.save_log_entry(is_adding, dirty_fields)

    class Meta:
        audit_log_fields = []


class GemCutConditionalMixin:
    def should_cut_on_save(self, *args, **kwargs):  # noqa
        return True

    def should_cut_on_delete(self, *args, **kwargs):  # noqa
        return True


class GemModelMixin(models.Model):
    cutting_started_at = models.DateTimeField(null=True, blank=True)
    cutting_completed_at = models.DateTimeField(null=True, blank=True)

    @classmethod
    def update_cutting_started_at(cls, ids: list):
        cls.objects.filter(id__in=ids).select_for_update().update(cutting_started_at=timezone.now())

    @classmethod
    def update_cutting_completed_at(cls, ids: list):
        cls.objects.filter(id__in=ids).select_for_update().update(
            cutting_completed_at=timezone.now()
        )

    @property
    def is_cutting_in_progress(self):
        return (
            self.cutting_started_at
            and self.cutting_completed_at
            and self.cutting_started_at > self.cutting_completed_at
        )

    class Meta:
        abstract = True
