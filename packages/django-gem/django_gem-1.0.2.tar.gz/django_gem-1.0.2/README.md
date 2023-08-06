# Django Gem

Django-gem is a reusable Django package that allows user to offload on-the-fly calculations
for Django models by putting them into database and providing and easy to use architecture to define,
how and when those database fields need to be refreshed.

### Installation

---
Using `pip`
<pre>pip install django-gem</pre>

Using `poetry`
<pre>poetry add django-gem</pre>

---

Then add 'django_gem' to your INSTALLED_APPS.
<pre>
INSTALLED_APPS = [
    ...
    'django_gem',
]
</pre>

---

Usage

First you will need to create a class that knows how to re-calculate your database fields.
In this package those classes are called "Cutters".

Each of the methods on the cutter need to be defined as `property`,
and the names of those methods should mirror re-calculated fields on the Gem model in the format of `cut_<field_name>`.

Side effects on the properties define what related models should trigger recalculations on those fields.

```python
from django_gems_example.gems.callbacks.author import AuthorCutterCallbacks
from django_gems_example.models import Author, Book

from django_gem.cutters.base import BaseCutter
from django_gem.decorators.cutters import side_effects


class AuthorCutter(BaseCutter):
    instance: Author

    @property
    @side_effects(
        (Author, [], AuthorCutterCallbacks.author),
        (Book, ["author"], AuthorCutterCallbacks.book_author),
    )
    def cut_book_count(self):
        return self.instance.books.count()
```

Django-gem allows you to create a "satellite" model for you main one,
and define the `CutterEngineMeta` with the created `cutter`.

```python

from django.db import models
from django_gems_example.gems.cutters.author import AuthorCutter
from django_gems_example.models import Author

from django_gem.models.base import CutterEngineBaseModel, CutterEngineMetaBase


class AuthorGem(CutterEngineBaseModel):
    book_count = models.IntegerField(default=0)

    class CutterEngineMeta(CutterEngineMetaBase):
        model = Author
        cutter = AuthorCutter

```

To access these fields from the main model, you need to define a property on the model with the same name as
the Gem field name, and wrap it with a `gem_property` decorator.

```python

from django.db import models

from django_gem.decorators import gem_property


class Author(models.Model):
    name = models.CharField(max_length=100)

    @gem_property
    def book_count(self):
        return self.gem.book_count

```

---

All the calculations happen implicitly, as `cutter_registry` that is populated on Django app startup
loads all the related models and attaches hooks for calculation. But, if needed, there are methods that you can
invoke directly from the `Saw` class. It allows refreshing a model, a queryset or an entire content type.
