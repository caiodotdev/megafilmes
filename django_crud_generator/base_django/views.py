#! -*- coding: UTF-8 -*-
from django.views import generic
from django.core import paginator
from django.contrib.admin.utils import NestedObjects
from django.contrib import messages
from django.core.exceptions import FieldDoesNotExist

from . import conf as base_conf


class BaseView(object):

    def __init__(self, model=None):
        if model:
            self.model = model

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


class BaseCreateView(BaseView, generic.CreateView):
    """
    View based on CreateView from django.views.generic.
    Use a custom template for a form display
    """
    template_name = "create.html"

    def get_context_data(self, **kwargs):
        context = super(BaseCreateView, self).get_context_data(**kwargs)

        if self.model:
            context['model_name'] = self.model._meta.verbose_name.title()
            context['model_name_plural'] = self.model._meta.verbose_name_plural.title()

        return context


class BaseUpdateView(BaseView, generic.UpdateView):
    """
    View based on Update from django.views.generic.
    Use a custom template for a form display
    """
    template_name = "update.html"
    context_object_name = "element"

    def get_context_data(self, **kwargs):
        context = super(BaseUpdateView, self).get_context_data(**kwargs)

        if self.model:
            context['model_name'] = self.model._meta.verbose_name.title()
            context['model_name_plural'] = self.model._meta.verbose_name_plural.title()

        return context


class SimpleFilterMixin(object):

    def get_queryset(self):
        self.queryset = super(SimpleFilterMixin, self).get_queryset()
        new_args = dict()
        for key, value in self.request.GET.items():
            print(key, value)
            new_args.update({
                "{}__icontains".format(key): value
            })
        self.queryset = self.queryset.filter(**new_args)

        return self.queryset


class BaseListView(BaseView, generic.ListView):
    """
    View based on ListView from django.views.generic.
    Use a custom template for iterate a list
    """
    template_name = "list.html"
    context_object_name = "list"

    def get_context_data(self, **kwargs):
        context = super(BaseListView, self).get_context_data(**kwargs)

        context['model_name'] = self.get_queryset().model._meta.verbose_name.title()
        context['model_name_plural'] = self.get_queryset().model._meta.verbose_name_plural.title()

        return context


class BasePaginationListView(BaseView, generic.ListView):
    """
    View based on ListView from django.views.generic.
    Use a custom template for iterate a list.
    Uses django.core.paginator to slice the result in pages
    """
    template_name = "pagination_list.html"
    context_object_name = "list"

    def get_context_data(self, **kwargs):
        context = super(BasePaginationListView, self).get_context_data(**kwargs)

        queryset = self.get_queryset()
        if not queryset.ordered:
            queryset = queryset.order_by("id")

        recordings_by_page = base_conf.ITEMS_BY_PAGE
        pager = paginator.Paginator(queryset, recordings_by_page)
        page = self.request.GET.get('page', 1)
        try:
            recordings = pager.page(page)

            start_index = max(1, recordings.number - 3)
            end_index = min(recordings.number + 3, (len(queryset) // recordings_by_page) + 1)
            context['range'] = range(start_index, end_index + 1)
            context[self.context_object_name] = recordings
        except paginator.PageNotAnInteger:
            context[self.context_object_name] = pager.page(1)
        except paginator.EmptyPage:
            context[self.context_object_name] = pager.page(pager.num_pages)

        if len(self.get_queryset()) > 0:
            context['model_name'] = self.get_queryset()[0]._meta.verbose_name.title()
            context['model_name_plural'] = self.get_queryset()[0]._meta.verbose_name_plural.title()

        return context


class BaseGridView(BaseListView):
    """
    View based on ListView from django.views.generic.
    Use a custom template for iterate a list in a grid
    """
    template_name = "grid.html"


class BasePaginationGridView(BasePaginationListView):
    """
    View based on ListView from django.views.generic.
    Use a custom template for iterate a list in a grid
    Uses django.core.paginator to slice the result in pages
    """
    template_name = "pagination_grid.html"


class BaseDetailView(BaseView, generic.DetailView):
    """
    View based on DetailView from django.views.generic.
    Shows all attributes and values of an object
    """
    template_name = "detail.html"
    context_object_name = "element"

    def get_context_data(self, **kwargs):
        context = super(BaseDetailView, self).get_context_data(**kwargs)

        if self.model:
            context['model_name'] = self.model._meta.verbose_name.title()
            context['model_name_plural'] = self.model._meta.verbose_name_plural.title()

        return context


class BaseDeleteView(BaseView, generic.DeleteView):
    """
    View based on Delete view from django.views.generic
    Show a list with all elements to be delete and delete it on post
    """
    template_name = "delete.html"
    context_object_name = "object"

    def get_context_data(self, **kwargs):
        context = super(BaseDeleteView, self).get_context_data(**kwargs)

        collector = NestedObjects(using='default')
        collector.collect([self.get_object()])
        context['deleted_objects'] = collector.nested()

        if self.model:
            context['model_name'] = self.model._meta.verbose_name.title()
            context['model_name_plural'] = self.model._meta.verbose_name_plural.title()

        return context
