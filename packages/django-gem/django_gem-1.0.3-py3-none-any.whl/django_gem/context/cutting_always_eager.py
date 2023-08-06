from django_gem.entities.context import gem_cutting_context


class CuttingAlwaysEager:
    def __enter__(self):
        gem_cutting_context.return_eager_value = True

    def __exit__(self, exc_type, exc_value, exc_traceback):
        gem_cutting_context.return_eager_value = False
