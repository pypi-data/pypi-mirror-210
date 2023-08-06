from celery import shared_task


@shared_task(name="cut_content_type_task")
def cut_content_type_task(content_type_id: int, field_names: list):
    from django_gem.toolkit.saw import Saw

    Saw.cut_content_type(content_type_id, field_names)
