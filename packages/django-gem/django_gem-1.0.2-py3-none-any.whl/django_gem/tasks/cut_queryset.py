from celery import shared_task


@shared_task(name="cut_queryset_task")
def cut_queryset_task(content_type_id: int, object_ids: list):
    from django_gem.toolkit.saw import Saw

    Saw.cut_queryset(content_type_id, object_ids)
