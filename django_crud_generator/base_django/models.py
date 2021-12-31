from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.text import slugify
from django.contrib.admin.utils import NestedObjects

from . import (
    utils,
    conf
)


class DisplayFieldsMixin(object):

    visible_fields = None

    def display_fields(self):
        if self.visible_fields is not None:
            return (x for x in self._meta.fields if x.name in self.visible_fields)
        else:
            return self._meta.fields

    def get_fields(self):
        """
        Iterates over the model and return all fields and values
        :return: Array of tuples. Each tuple is (parameter, value of parameter)
        """
        return [(_(field.verbose_name), field.value_to_string(self)) for field in self.display_fields()]

    def get_related_fields(self, using="default"):
        collector = NestedObjects(using=using)
        collector.collect([self])
        return collector.instances_with_model()


class BaseModel(models.Model, DisplayFieldsMixin):
    """
    Default base models
    """

    class Meta:
        abstract = True


class SimpleBaseModel(BaseModel):
    """
    Simple model model, includes a name and description
    """
    name = models.CharField(max_length=100, blank=True, verbose_name=conf.BASE_MODELS_TRANSLATION_NAME)
    description = models.TextField(blank=True, verbose_name=conf.BASE_MODELS_TRANSLATION_DESCRIPTION)

    class Meta:
        abstract = True

    def __str__(self):
        return self.name


class ModifiableBaseModel(BaseModel):
    """
    Simple base model to timestamp fields, created and modified included
    """
    created = models.DateTimeField(auto_now_add=True, verbose_name=conf.BASE_MODELS_TRANSLATION_CREATED)
    modified = models.DateTimeField(auto_now=True, verbose_name=conf.BASE_MODELS_TRANSLATION_MODIFIED)

    class Meta:
        abstract = True

    def __str__(self):
        return str(self.created)


class RemovableBaseModel(ModifiableBaseModel):
    """
    Simple base model, to check active objects, include an active flag
    """
    active = models.BooleanField(default=True, verbose_name=conf.BASE_MODELS_TRANSLATION_ACTIVE)

    class Meta:
        abstract = True

    def __str__(self):
        return self.id


class FullBaseModel(BaseModel):
    """
    Complete model, includes a mixin for SimpleBaseModel, ModifiableBaseModel and RemovableBaseModel
    """
    name = models.CharField(max_length=100, blank=True, verbose_name=conf.BASE_MODELS_TRANSLATION_NAME)
    description = models.TextField(blank=True, verbose_name=conf.BASE_MODELS_TRANSLATION_DESCRIPTION)
    created = models.DateTimeField(auto_now_add=True, verbose_name=conf.BASE_MODELS_TRANSLATION_CREATED)
    modified = models.DateTimeField(auto_now=True, verbose_name=conf.BASE_MODELS_TRANSLATION_MODIFIED)
    active = models.BooleanField(default=True, verbose_name=conf.BASE_MODELS_TRANSLATION_ACTIVE)

    class Meta:
        abstract = True

    def __str__(self):
        return self.name


class FullSlugBaseModel(BaseModel):
    """
    Complete model, includes the same from FullBaseModel and a slug field, to reference in URL in Class Based Views
    """
    name = models.CharField(max_length=100, blank=True, verbose_name=conf.BASE_MODELS_TRANSLATION_NAME)
    description = models.TextField(blank=True, verbose_name=conf.BASE_MODELS_TRANSLATION_DESCRIPTION)
    slug = models.SlugField(blank=True, unique=True, verbose_name=conf.BASE_MODELS_TRANSLATION_SLUG)
    created = models.DateTimeField(auto_now_add=True, verbose_name=conf.BASE_MODELS_TRANSLATION_CREATED)
    modified = models.DateTimeField(auto_now=True, verbose_name=conf.BASE_MODELS_TRANSLATION_MODIFIED)
    active = models.BooleanField(default=True, verbose_name=conf.BASE_MODELS_TRANSLATION_ACTIVE)
    SLUG_RANDOM_CHARS = 20
    MAX_RANDOM_TRIES = 5

    class Meta:
        abstract = True

    def generate_valid_random_slug(self):
        slug = slugify(str(self))
        valid_slug = False

        index_iterations = 0
        while not valid_slug and index_iterations < self.MAX_RANDOM_TRIES:
            index_iterations += 1
            if len(slug) + self.SLUG_RANDOM_CHARS > 50:
                slug = slug[:49][:-self.SLUG_RANDOM_CHARS] + "-" + utils.generate_random_string(
                    self.SLUG_RANDOM_CHARS)
            else:
                slug = slug + "-" + utils.generate_random_string(self.SLUG_RANDOM_CHARS)

            if index_iterations == self.MAX_RANDOM_TRIES:
                return slug
            valid_slug = type(self).objects.filter(slug=slug).count() == 0
        return slug

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        """
        Custom save method, it checks if slug is unique and define a valid unique slug
        :param force_insert:  Might force the insert
        :param force_update: Might force the update
        :param using: Object using
        :param update_fields: Fields to be updated
        :return: Object
        """
        if not self.slug:
            self.slug = self.generate_valid_random_slug()
        super(FullSlugBaseModel, self).save(force_insert, force_update, using, update_fields)

    def __str__(self):
        return self.name
