#!/usr/bin/env python
# -*- coding: utf-8 -*-
import requests
from django.contrib import messages
from django.contrib.admin.utils import NestedObjects
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.exceptions import FieldDoesNotExist
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import redirect
from django.views.generic.detail import DetailView
from django.views.generic.edit import (
    CreateView, DeleteView, UpdateView
)
from django.views.generic.list import ListView

from django.db.models import Q

try:
    from django.core.urlresolvers import reverse_lazy
except ImportError:
    from django.urls import reverse_lazy, reverse

from app.models import Channel, Program
from app.forms import ChannelForm
from app.mixins import ChannelMixin
from app.conf import CHANNEL_DETAIL_URL_NAME, CHANNEL_LIST_URL_NAME

from django_datatables_view.base_datatable_view import BaseDatatableView

from app.utils import upload_image, upload_file, get_articles, find_program, get_program_content

import django_filters


class ChannelFormSetManagement(object):
    formsets = []

    def form_valid(self, form):
        context = self.get_context_data()
        with transaction.atomic():
            self.object = form.save()

            for Formset in self.formsets:
                formset = context["{}set".format(str(Formset.model.__name__).lower())]
                if formset.is_valid():
                    formset.instance = self.object
                    formset.save()
        return super(ChannelFormSetManagement, self).form_valid(form)

    def get_context_data(self, **kwargs):
        data = super(ChannelFormSetManagement, self).get_context_data(**kwargs)
        for Formset in self.formsets:
            if self.request.POST:
                data["{}set".format(str(Formset.model.__name__).lower())] = Formset(self.request.POST,
                                                                                    self.request.FILES,
                                                                                    instance=self.object)
            else:
                data["{}set".format(str(Formset.model.__name__).lower())] = Formset(instance=self.object)
        return data


class ChannelFilter(django_filters.FilterSet):
    class Meta:
        model = Channel
        fields = ["id", "title", "image", "url"]


class List(LoginRequiredMixin, ChannelMixin, ListView):
    """
    List all Channels
    """
    login_url = '/admin/login/'
    template_name = 'channel/list.html'
    model = Channel
    context_object_name = 'channels'
    paginate_by = 1

    def get_context_data(self, **kwargs):
        context = super(List, self).get_context_data(**kwargs)
        queryset = self.get_queryset()
        filter = ChannelFilter(self.request.GET, queryset)
        context["filter"] = filter
        return context


class ListFull(LoginRequiredMixin, ChannelMixin, ListView):
    """
    List all Channels
    """
    login_url = '/admin/login/'
    template_name = 'channel/list_full.html'
    model = Channel
    context_object_name = 'channels'
    ordering = '-id'
    paginate_by = 10
    search = ''

    def get_queryset(self):
        queryset = super().get_queryset()
        filter = ChannelFilter(self.request.GET, queryset)
        queryset = self.search_general(filter.qs)
        queryset = self.ordering_data(queryset)
        return queryset

    def search_general(self, qs):
        if 'search' in self.request.GET:
            self.search = self.request.GET['search']
            if self.search:
                search = self.search
                qs = qs.filter(Q(id__icontains=search) | Q(title__icontains=search) | Q(image__icontains=search) | Q(
                    url__icontains=search))
        return qs

    def get_ordering(self):
        if 'ordering' in self.request.GET:
            self.ordering = self.request.GET['ordering']
            if self.ordering:
                return self.ordering
            else:
                self.ordering = '-id'
        return self.ordering

    def ordering_data(self, qs):
        qs = qs.order_by(self.get_ordering())
        return qs

    def get_context_data(self, **kwargs):
        context = super(ListFull, self).get_context_data(**kwargs)
        queryset = self.get_queryset()
        filter = ChannelFilter(self.request.GET, queryset)
        page_size = self.get_paginate_by(queryset)
        if page_size:
            paginator, page, queryset, is_paginated = self.paginate_queryset(queryset, page_size)
            context.update(**{
                'ordering': self.ordering,
                'search': self.search,
                'filter': filter,
                'paginator': paginator,
                'page_obj': page,
                'is_paginated': is_paginated,
                'object_list': queryset
            })
        else:
            context.update(**{
                'search': self.search,
                'ordering': self.ordering,
                'filter': filter,
                'paginator': None,
                'page_obj': None,
                'is_paginated': False,
                'object_list': queryset
            })
        return context


class Create(LoginRequiredMixin, ChannelMixin, PermissionRequiredMixin, ChannelFormSetManagement, CreateView):
    """
    Create a Channel
    """
    login_url = '/admin/login/'
    model = Channel
    permission_required = (
        'app.add_channel'
    )
    form_class = ChannelForm
    template_name = 'channel/create.html'
    context_object_name = 'channel'

    def get_context_data(self, **kwargs):
        context = super(Create, self).get_context_data(**kwargs)
        return context

    def get_success_url(self):
        return reverse_lazy(CHANNEL_DETAIL_URL_NAME, kwargs=self.kwargs_for_reverse_url())

    def get_initial(self):
        data = super(Create, self).get_initial()
        return data

    def form_valid(self, form):
        messages.success(self.request, 'Channel criado com sucesso')
        return super(Create, self).form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Houve algum erro, tente novamente')
        return super(Create, self).form_invalid(form)


class Detail(LoginRequiredMixin, ChannelMixin, DetailView):
    """
    Detail of a Channel
    """
    login_url = '/admin/login/'
    model = Channel
    template_name = 'channel/detail.html'
    context_object_name = 'channel'

    def get_context_data(self, **kwargs):
        context = super(Detail, self).get_context_data(**kwargs)
        return context


class Update(LoginRequiredMixin, ChannelMixin, PermissionRequiredMixin, ChannelFormSetManagement, UpdateView):
    """
    Update a Channel
    """
    login_url = '/admin/login/'
    model = Channel
    template_name = 'channel/update.html'
    context_object_name = 'channel'
    form_class = ChannelForm
    permission_required = (
        'app.change_channel'
    )

    def get_initial(self):
        data = super(Update, self).get_initial()
        return data

    def get_success_url(self):
        return reverse_lazy(CHANNEL_DETAIL_URL_NAME, kwargs=self.kwargs_for_reverse_url())

    def get_context_data(self, **kwargs):
        data = super(Update, self).get_context_data(**kwargs)
        return data

    def form_valid(self, form):
        messages.success(self.request, 'Channel atualizado com sucesso')
        return super(Update, self).form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Houve algum erro, tente novamente')
        return super(Update, self).form_invalid(form)


class Delete(LoginRequiredMixin, ChannelMixin, PermissionRequiredMixin, DeleteView):
    """
    Delete a Channel
    """
    login_url = '/admin/login/'
    model = Channel
    permission_required = (
        'app.delete_channel'
    )
    template_name = 'channel/delete.html'
    context_object_name = 'channel'

    def get_context_data(self, **kwargs):
        context = super(Delete, self).get_context_data(**kwargs)
        collector = NestedObjects(using='default')
        collector.collect([self.get_object()])
        context['deleted_objects'] = collector.nested()
        return context

    def __init__(self):
        super(Delete, self).__init__()

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Channel removido com sucesso')
        return super(Delete, self).delete(self.request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy(CHANNEL_LIST_URL_NAME)


class ChannelListJson(BaseDatatableView):
    model = Channel
    columns = ("id", "title", "image", "url", "program")
    order_columns = ["id", "title", "image", "url"]
    max_display_length = 500

    def render_column(self, row, column):
        if column == 'program':
            if row.program:
                return row.program.url
            url, logo = find_program(row.title)
            prog = Program()
            prog.title = row.title
            prog.url = url
            prog.save()
            row.program = prog
            row.save()
            return url
        else:
            return super(ChannelListJson, self).render_column(row, column)

    def filter_queryset(self, qs):
        search = self.request.GET.get('search[value]', None)
        if search:
            qs = qs.filter(Q(id__icontains=search) | Q(title__icontains=search) | Q(image__icontains=search) | Q(
                url__icontains=search))
        filter = ChannelFilter(self.request.GET, qs)
        return filter.qs


def delete_all_channels(request):
    Channel.objects.all().delete()
    return redirect('CHANNEL_list')


def get_channels(request):
    url_channels = 'https://megafilmeshdd.org/categoria/canais/page/{}'

    def title_exists(title):
        return Channel.objects.filter(title=title).exists()

    def save_channel(title, rating, image, data_lancamento, url_serie):
        data = {
            "title": title,
            "image": image,
            "url": url_serie
        }
        req = requests.post('https://megafilmes.herokuapp.com/api/channel/', data=data)
        if req.status_code != 201:
            print(req.status_code)
            print('---- erro ao inserir channel')
        # channel = Channel()
        # channel.title = title
        # channel.image = image
        # channel.url = url_serie
        # channel.save()

    return get_articles(url_channels, 5, {'class': 'items'}, save_channel, title_exists)


def get_content_url(request):
    id = request.GET['id']
    channel = Channel.objects.get(id=id)
    return JsonResponse({'content': get_program_content(channel.program.url)})
