from django.contrib.contenttypes.models import ContentType
from django.db import models

from django_gem.constants import GemLogEntryAction


class GemLogEntryManager(models.Manager):
    def log_create(self, instance, **kwargs):
        changes = kwargs.get("changes", None)
        pk = self._get_pk_value(instance)

        content_type = ContentType.objects.get_for_model(instance)

        if changes is not None:
            kwargs.setdefault("content_type", content_type)
            kwargs.setdefault("object_id", pk)

            if kwargs.get("action", None) is GemLogEntryAction.CREATE:
                self.filter(content_type=content_type, object_id=pk).delete()
            return self.create(**kwargs)
        return None

    def _get_pk_value(self, instance):
        """
        Get the primary key field value for a model instance.

        :param instance: The model instance to get the primary key for.
        :type instance: Model
        :return: The primary key value of the given model instance.
        """
        pk_field = instance._meta.pk.name  # noqa
        pk = getattr(instance, pk_field, None)

        # Check to make sure that we got a pk not a model object.
        if isinstance(pk, models.Model):
            pk = self._get_pk_value(pk)
        return pk
