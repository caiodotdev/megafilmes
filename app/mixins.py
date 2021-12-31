from app.models import (
    Movie
)
from django.core.exceptions import FieldDoesNotExist

class MovieMixin(object):

    def kwargs_for_reverse_url(self):
        kwargs_dict = dict()
        if self.model:
            self.object = self.object if self.object is not None else self.get_object()
            try:
                self.model._meta.get_field('slug')
                kwargs_dict['slug'] = self.object.slug
            except FieldDoesNotExist:
                kwargs_dict['pk'] = self.object.id
        return kwargs_dict

    def get_context_data(self, **kwargs):
        context = super(MovieMixin, self).get_context_data(**kwargs)
        if self.model:
            context['model_name'] = self.model._meta.verbose_name.title()
            context['model_name_plural'] = self.model._meta.verbose_name_plural.title()
        return context

    def get_movie(self):
        return Movie.objects.get(pk=self.kwargs.get("pk_movie", 0))

class SerieMixin(object):

    def kwargs_for_reverse_url(self):
        kwargs_dict = dict()
        if self.model:
            self.object = self.object if self.object is not None else self.get_object()
            try:
                self.model._meta.get_field('slug')
                kwargs_dict['slug'] = self.object.slug
            except FieldDoesNotExist:
                kwargs_dict['pk'] = self.object.id
        return kwargs_dict

    def get_context_data(self, **kwargs):
        context = super(SerieMixin, self).get_context_data(**kwargs)
        if self.model:
            context['model_name'] = self.model._meta.verbose_name.title()
            context['model_name_plural'] = self.model._meta.verbose_name_plural.title()
        return context

    def get_serie(self):
        return Serie.objects.get(pk=self.kwargs.get("pk_serie", 0))

class ChannelMixin(object):

    def kwargs_for_reverse_url(self):
        kwargs_dict = dict()
        if self.model:
            self.object = self.object if self.object is not None else self.get_object()
            try:
                self.model._meta.get_field('slug')
                kwargs_dict['slug'] = self.object.slug
            except FieldDoesNotExist:
                kwargs_dict['pk'] = self.object.id
        return kwargs_dict

    def get_context_data(self, **kwargs):
        context = super(ChannelMixin, self).get_context_data(**kwargs)
        if self.model:
            context['model_name'] = self.model._meta.verbose_name.title()
            context['model_name_plural'] = self.model._meta.verbose_name_plural.title()
        return context

    def get_channel(self):
        return Channel.objects.get(pk=self.kwargs.get("pk_channel", 0))

