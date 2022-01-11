#!/usr/bin/env python
# -*- coding: utf-8 -*-
import requests
from django.contrib import messages
from django.contrib.admin.utils import NestedObjects
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.exceptions import FieldDoesNotExist
from django.db import transaction
from django.shortcuts import redirect
from django.views.generic import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import (
    CreateView, DeleteView, UpdateView
)
from django.views.generic.list import ListView

from django.db.models import Q

from app.views.link import MegaPack

try:
    from django.core.urlresolvers import reverse_lazy
except ImportError:
    from django.urls import reverse_lazy, reverse

from app.models import Serie, Playlist, UrlPlaylist
from app.forms import SerieForm
from app.mixins import SerieMixin
from app.conf import SERIE_DETAIL_URL_NAME, SERIE_LIST_URL_NAME

from django_datatables_view.base_datatable_view import BaseDatatableView

from app.utils import upload_image, upload_file, get_articles, get_page

import django_filters


class SerieFormSetManagement(object):
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
        return super(SerieFormSetManagement, self).form_valid(form)

    def get_context_data(self, **kwargs):
        data = super(SerieFormSetManagement, self).get_context_data(**kwargs)
        for Formset in self.formsets:
            if self.request.POST:
                data["{}set".format(str(Formset.model.__name__).lower())] = Formset(self.request.POST,
                                                                                    self.request.FILES,
                                                                                    instance=self.object)
            else:
                data["{}set".format(str(Formset.model.__name__).lower())] = Formset(instance=self.object)
        return data


class SerieFilter(django_filters.FilterSet):
    class Meta:
        model = Serie
        fields = ["id", "title", "year", "rating", "image", "url"]


class List(LoginRequiredMixin, SerieMixin, ListView):
    """
    List all Series
    """
    login_url = '/admin/login/'
    template_name = 'serie/list.html'
    model = Serie
    context_object_name = 'series'
    paginate_by = 1

    def get_context_data(self, **kwargs):
        context = super(List, self).get_context_data(**kwargs)
        queryset = self.get_queryset()
        filter = SerieFilter(self.request.GET, queryset)
        context["filter"] = filter
        return context


class ListFull(LoginRequiredMixin, SerieMixin, ListView):
    """
    List all Series
    """
    login_url = '/admin/login/'
    template_name = 'serie/list_full.html'
    model = Serie
    context_object_name = 'series'
    ordering = '-id'
    paginate_by = 10
    search = ''

    def get_queryset(self):
        queryset = super().get_queryset()
        filter = SerieFilter(self.request.GET, queryset)
        queryset = self.search_general(filter.qs)
        queryset = self.ordering_data(queryset)
        return queryset

    def search_general(self, qs):
        if 'search' in self.request.GET:
            self.search = self.request.GET['search']
            if self.search:
                search = self.search
                qs = qs.filter(Q(id__icontains=search) | Q(title__icontains=search) | Q(year__icontains=search) | Q(
                    rating__icontains=search) | Q(image__icontains=search) | Q(url__icontains=search))
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
        filter = SerieFilter(self.request.GET, queryset)
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


class Create(LoginRequiredMixin, SerieMixin, PermissionRequiredMixin, SerieFormSetManagement, CreateView):
    """
    Create a Serie
    """
    login_url = '/admin/login/'
    model = Serie
    permission_required = (
        'app.add_serie'
    )
    form_class = SerieForm
    template_name = 'serie/create.html'
    context_object_name = 'serie'

    def get_context_data(self, **kwargs):
        context = super(Create, self).get_context_data(**kwargs)
        return context

    def get_success_url(self):
        return reverse_lazy(SERIE_DETAIL_URL_NAME, kwargs=self.kwargs_for_reverse_url())

    def get_initial(self):
        data = super(Create, self).get_initial()
        return data

    def form_valid(self, form):
        messages.success(self.request, 'Serie criado com sucesso')
        return super(Create, self).form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Houve algum erro, tente novamente')
        return super(Create, self).form_invalid(form)


def check_url_assistido(serie, url):
    for p in serie.playlist_set.all():
        for u in p.urlplaylist_set.all():
            if u.url == url:
                return True
    return False


class Detail(LoginRequiredMixin, SerieMixin, DetailView):
    """
    Detail of a Serie
    """
    login_url = '/admin/login/'
    model = Serie
    template_name = 'serie/detail.html'
    context_object_name = 'serie'

    def get_episodes(self):
        result = []
        object = self.get_object()
        page = get_page(self.object.url, {})
        if page:
            episodios = page.findAll('ul', {'class': 'episodios'})
            for temp in episodios:
                try:
                    list = temp.findAll('li')
                    if len(list) > 0:
                        for li in temp.findAll('li'):
                            link_url = li.find('div', {'class': 'episodiotitle'}).find('a')['href']
                            result.append({
                                'image': li.find('div', {'class': 'imagen'}).find('img')['src'],
                                'number': li.find('div', {'class': 'numerando'}).text,
                                'title': li.find('div', {'class': 'episodiotitle'}).find('a').text,
                                'link': link_url,
                                'date': li.find('div', {'class': 'episodiotitle'}).find('span').text,
                                'assistido': check_url_assistido(object, link_url)
                            })
                except (Exception,):
                    print('-- nao foi possivel preencher os episodios desta serie')
        return result

    def get_context_data(self, **kwargs):
        context = super(Detail, self).get_context_data(**kwargs)
        context['episodios'] = self.get_episodes()
        return context


class Episode(LoginRequiredMixin, TemplateView):
    """
    Detail of a Serie
    """
    login_url = '/admin/login/'
    template_name = 'serie/episode.html'

    def get_title(self, link: str):
        episodios = 'episodios'
        if episodios in link:
            return link[link.index(episodios) + len(episodios):]
        return link

    def get_context_data(self, **kwargs):
        context = super(Episode, self).get_context_data(**kwargs)
        serie = Serie.objects.get(id=self.request.GET['serie'])
        if 'link' in self.request.GET:
            url_playlist = self.request.GET['link']
            playlist = Playlist()
            playlist.serie = serie
            playlist.titulos = self.get_title(url_playlist)
            playlist.save()
            urlp = UrlPlaylist()
            urlp.url = url_playlist
            urlp.playlist = playlist
            urlp.save()
            mega = MegaPack(url_playlist)
            url_playlist = mega.get_info()
            context['m3u8'] = url_playlist
            return context
        if 'links' in self.request.GET:
            links = self.request.GET.getlist('links')
            playlist = Playlist()
            playlist.serie = serie
            playlist.save()
            for url_playlist in links:
                title = self.get_title(url_playlist)
                playlist.titulos = playlist.titulos + '\n' + title
                playlist.save()
                urlp = UrlPlaylist()
                urlp.url = url_playlist
                urlp.playlist = playlist
                urlp.save()
        if 'playlist' in self.request.GET:
            playlist = Playlist.objects.get(id=self.request.GET['playlist'])
        else:
            playlist = Playlist.objects.last()
        url_playlist = playlist.urlplaylist_set.first()
        mega = MegaPack(url_playlist.url)
        new_link = mega.get_info()
        url_playlist.playlist = None
        url_playlist.save()
        context['serie'] = serie
        context['m3u8'] = new_link
        if len(playlist.urlplaylist_set.all()) > 0:
            context['playlist'] = playlist.id
        return context


class Update(LoginRequiredMixin, SerieMixin, PermissionRequiredMixin, SerieFormSetManagement, UpdateView):
    """
    Update a Serie
    """
    login_url = '/admin/login/'
    model = Serie
    template_name = 'serie/update.html'
    context_object_name = 'serie'
    form_class = SerieForm
    permission_required = (
        'app.change_serie'
    )

    def get_initial(self):
        data = super(Update, self).get_initial()
        return data

    def get_success_url(self):
        return reverse_lazy(SERIE_DETAIL_URL_NAME, kwargs=self.kwargs_for_reverse_url())

    def get_context_data(self, **kwargs):
        data = super(Update, self).get_context_data(**kwargs)
        return data

    def form_valid(self, form):
        messages.success(self.request, 'Serie atualizado com sucesso')
        return super(Update, self).form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Houve algum erro, tente novamente')
        return super(Update, self).form_invalid(form)


class Delete(LoginRequiredMixin, SerieMixin, PermissionRequiredMixin, DeleteView):
    """
    Delete a Serie
    """
    login_url = '/admin/login/'
    model = Serie
    permission_required = (
        'app.delete_serie'
    )
    template_name = 'serie/delete.html'
    context_object_name = 'serie'

    def get_context_data(self, **kwargs):
        context = super(Delete, self).get_context_data(**kwargs)
        collector = NestedObjects(using='default')
        collector.collect([self.get_object()])
        context['deleted_objects'] = collector.nested()
        return context

    def __init__(self):
        super(Delete, self).__init__()

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Serie removido com sucesso')
        return super(Delete, self).delete(self.request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy(SERIE_LIST_URL_NAME)


class SerieListJson(BaseDatatableView):
    model = Serie
    columns = ("id", "image", "title", "year", "rating")
    order_columns = ["id", "image", "title", "year", "rating"]
    max_display_length = 500

    def filter_queryset(self, qs):
        search = self.request.GET.get('search[value]', None)
        if search:
            qs = qs.filter(Q(id__icontains=search) | Q(title__icontains=search) | Q(year__icontains=search) | Q(
                rating__icontains=search) | Q(image__icontains=search) | Q(url__icontains=search))
        filter = SerieFilter(self.request.GET, qs)
        return filter.qs


def delete_all_series(request):
    Serie.objects.all().delete()
    return redirect('SERIE_list')


def get_series(request):
    url_series = 'https://megafilmeshdd.org/series/page/{}'

    def title_exists(title):
        return Serie.objects.filter(title=title).exists()

    def save_serie(title, rating, image, data_lancamento, url_serie):
        serie = Serie()
        serie.title = title
        serie.rating = rating
        serie.image = image
        serie.year = data_lancamento
        serie.url = url_serie
        serie.save()

    return get_articles(url_series, 48, {'id': 'archive-content'}, save_serie, title_exists)
