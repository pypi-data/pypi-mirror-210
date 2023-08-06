from celery import shared_task


@shared_task(name="cut_models_task")
def cut_models_task(sealed_chest: str):
    from django_gem.toolkit.saw import Saw

    Saw.cut_models(sealed_chest)
