#!/usr/bin/env python
# -*- coding: utf-8 -*-
from http import HTTPStatus

import requests
import unidecode
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

from app.views.megapack import MegaPack
from app.views.movie import remove_accents

try:
    from django.core.urlresolvers import reverse_lazy
except ImportError:
    from django.urls import reverse_lazy, reverse

from app.models import Serie, Playlist, UrlPlaylist, Episodio
from app.mixins import SerieMixin

from django_datatables_view.base_datatable_view import BaseDatatableView

from app.utils import get_articles, get_page, HEADERS_MEGA

import django_filters


class SerieFilter(django_filters.FilterSet):
    class Meta:
        model = Serie
        fields = ["title", "year", "rating", ]


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
        # get_m3u8_episodes({}, mega=MegaPack())
        context = super(List, self).get_context_data(**kwargs)
        queryset = self.get_queryset()
        filter = SerieFilter(self.request.GET, queryset)
        context["filter"] = filter
        return context


class EpisodioFilter(django_filters.FilterSet):
    class Meta:
        model = Episodio
        fields = ["title", ]


class ListSelected(LoginRequiredMixin, SerieMixin, ListView):
    """
    List all Series
    """
    login_url = '/admin/login/'
    template_name = 'serie/list_selected.html'
    model = Episodio
    queryset = Episodio.objects.filter(selected=True)
    context_object_name = 'episodios'
    ordering = 'id'
    paginate_by = 10
    search = ''

    def get_queryset(self):
        queryset = Episodio.objects.filter(selected=True)
        filter = EpisodioFilter(self.request.GET, queryset)
        queryset = self.search_general(filter.qs)
        queryset = self.ordering_data(queryset)
        return queryset

    def search_general(self, qs):
        if 'search' in self.request.GET:
            self.search = self.request.GET['search']
            if self.search:
                search = self.search
                qs = qs.filter(Q(id__icontains=search) | Q(title__icontains=search))
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
        context = super(ListSelected, self).get_context_data(**kwargs)
        queryset = self.get_queryset()
        filter = EpisodioFilter(self.request.GET, queryset)
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


def check_url_assistido(serie, url):
    for p in serie.playlist_set.all():
        for u in p.urlplaylist_set.all():
            if u.url == url:
                return True
    return False


def get_episodes(object):
    page = get_page(object.url, HEADERS_MEGA)
    if page:
        episodios = page.findAll('ul', {'class': 'episodios'})
        for temp in episodios:
            try:
                list = temp.findAll('li')
                if len(list) > 0:
                    for li in temp.findAll('li'):
                        link_url = li.find('div', {'class': 'episodiotitle'}).find('a')['href']
                        ep = Episodio()
                        ep.image = li.find('div', {'class': 'imagen'}).find('img')['src']
                        ep.number = li.find('div', {'class': 'numerando'}).text
                        ep.title = li.find('div', {'class': 'episodiotitle'}).find('a').text
                        ep.url = link_url
                        ep.serie = object
                        ep.date = li.find('div', {'class': 'episodiotitle'}).find('span').text
                        ep.save()
            except (Exception,):
                print('-- nao foi possivel preencher os episodios desta serie:' + str(object.title))
                object.delete()
    return None


class Detail(LoginRequiredMixin, SerieMixin, DetailView):
    """
    Detail of a Serie
    """
    login_url = '/admin/login/'
    model = Serie
    template_name = 'serie/detail.html'
    context_object_name = 'serie'

    def get_context_data(self, **kwargs):
        context = super(Detail, self).get_context_data(**kwargs)
        return context


class Episode(LoginRequiredMixin, DetailView):
    """
    Detail of a Serie
    """
    login_url = '/admin/login/'
    template_name = 'serie/episode.html'
    model = Episodio
    context_object_name = 'episodio'

    def get_title(self, link: str):
        episodios = 'episodios'
        if episodios in link:
            return link[link.index(episodios) + len(episodios):]
        return link

    def get_object(self, queryset=None):
        if 'playlist' in self.request.GET:
            playlist = Playlist.objects.get(id=self.request.GET['playlist'])
            urlplaylist = playlist.urlplaylist_set.first()
            return Episodio.objects.get(url=urlplaylist.url)
        ids = self.request.GET.getlist('ids')
        return Episodio.objects.get(id=ids[0])

    def mark_assistido(self):
        object = self.get_object()
        object.is_assistido = True
        object.save()

    def get_context_data(self, **kwargs):
        self.mark_assistido()
        context = super(Episode, self).get_context_data(**kwargs)
        serie = Serie.objects.get(id=self.request.GET['serie'])
        if 'ids' in self.request.GET:
            ids = self.request.GET.getlist('ids')
            playlist = Playlist()
            playlist.serie = serie
            playlist.save()
            for id in ids:
                episodio = Episodio.objects.get(id=id)
                title = self.get_title(episodio.url)
                playlist.titulos = playlist.titulos + '\n' + title
                playlist.save()
                urlp = UrlPlaylist()
                urlp.url = episodio.url
                urlp.playlist = playlist
                urlp.save()
        if 'playlist' in self.request.GET:
            playlist = Playlist.objects.get(id=self.request.GET['playlist'])
        else:
            playlist = Playlist.objects.last()
        url_playlist = playlist.urlplaylist_set.first()
        new_link = get_m3u8_episodio(self.request, self.get_object())
        url_playlist.delete()
        context['serie'] = serie
        context['m3u8'] = new_link
        if len(playlist.urlplaylist_set.all()) > 0:
            context['playlist'] = playlist.id
        return context


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


def update_serie(request, pk):
    serie = Serie.objects.get(id=pk)
    serie.episodio_set.all().delete()
    get_episodes(serie)
    return redirect('SERIE_detail', **{'pk': serie.pk})


def get_series(request):
    url_series = 'https://megafilmeshdd.org/series/page/{}'

    def title_exists(title):
        qs = Serie.objects.filter(title=title)
        if qs.exists():
            return qs.first()
        return None

    def updator(serie):
        get_episodes(serie)

    def save_serie(title, rating, image, data_lancamento, url_serie):
        serie = Serie()
        serie.title = title
        serie.rating = rating
        serie.image = image
        serie.year = data_lancamento
        serie.url = url_serie
        serie.save()
        get_episodes(serie)

    return get_articles(url_series, 50, {'id': 'archive-content'}, save_serie, title_exists, updator)


def get_m3u8_episodio(request, episodio):
    mega = MegaPack()
    url_m3u8 = mega.get_info(episodio.url)['m3u8']
    episodio.link_m3u8 = url_m3u8
    episodio.save()
    mega.close()
    return url_m3u8


def generate_selected_episodes(request):
    ids = request.GET.getlist('ids')
    Episodio.objects.filter(selected=True).update(selected=False)
    f = open("episode-selected.m3u8", "a")
    f.truncate(0)
    f.write("#EXTM3U\n")
    for id in ids:
        episode = Episodio.objects.get(id=id)
        episode.selected = True
        episode.save()
        get_m3u8_episodio(request, episode)
    write_m3u8_series()
    updator_series_server()
    return JsonResponse({'message': 'ok'})


def write_m3u8_series():
    f = open("episode-selected.m3u8", "a")
    f.truncate(0)
    f.write("#EXTM3U\n")
    for episodio in Episodio.objects.filter(selected=True):
        title = unidecode.unidecode(remove_accents(str(episodio.number + ': ' + episodio.title)))
        f.write('#EXTINF:{}, tvg-id="{} - {}" tvg-name="{} - {}" tvg-logo="{}" group-title="{}",{}\n{}\n'.format(
            episodio.id,
            episodio.id,
            title,
            title,
            episodio.id,
            episodio.image,
            'Episodes',
            title,
            episodio.link_m3u8))
    f.close()


def get_list_episodes_m3u8(request):
    write_m3u8_series()
    fsock = open("episode-selected.m3u8", "rb")
    return HttpResponse(fsock, content_type='text')


def get_m3u8_episodes(request, mega: MegaPack = None):
    if not mega:
        mega = MegaPack()
    episodes = Episodio.objects.filter(selected=True)
    for episode in episodes:
        print('-- ', episode.title)
        try:
            episode.link_m3u8 = mega.get_info(episode.url)['m3u8']
            episode.save()
        except (Exception,):
            episode.link_m3u8 = None
            episode.save()
            print('--- err ao coletar link m3u8: ' + str(episode.title))
    return JsonResponse({'message': 'ok'})


def delete_all_episodes_server():
    list_episodes_server = requests.get(URL_ENDPOINT_EPISODE).json()
    if list_episodes_server:
        for episode_server in list_episodes_server:
            requests.delete(URL_ENDPOINT_EPISODE + episode_server['id'] + '/')


def updator_series_server():
    delete_all_episodes_server()
    for episodio in Episodio.objects.filter(selected=True):
        episodio_server = has_object(episodio, URL_ENDPOINT_EPISODE)
        if episodio_server:
            data = {
                "id": str(episodio.id),
                "image": str(episodio.image),
                "url": str(episodio.url),
                "link_m3u8": str(episodio.link_m3u8),
                "selected": True
            }
            obj_updated = update_episodio_remote(episodio_server, data)
            if not obj_updated:
                print('Not Updated: ' + str(episodio.title))
            else:
                print('Updated: ' + str(episodio.title))
        else:
            obj_created = create_episodio_remote(episodio)
            if obj_created:
                print('Created new episode: ' + str(episodio.title))


URL_ENDPOINT_EPISODE = 'https://megafilmes.herokuapp.com/api/episodio/'
URL_ENDPOINT_SERIE = 'https://megafilmes.herokuapp.com/api/serie/'


def has_object(object, endpoint):
    req = requests.get(endpoint + '?id=' + str(object.id)).json()
    if req:
        return req[0]
    return None


def update_episodio_remote(olddata, newdata):
    req = requests.patch(URL_ENDPOINT_EPISODE + str(olddata['id']) + '/', data=newdata)
    if req.status_code == 200:
        return req.json()
    return None


def create_episodio_remote(episodio):
    serie = create_serie_remote(episodio.serie)
    data = {
        "id": str(episodio.id),
        "title": str(episodio.title),
        "image": str(episodio.image),
        "url": str(episodio.url),
        "link_m3u8": str(episodio.link_m3u8),
        "serie": str(serie['id']),
        "selected": True
    }
    req = requests.post(URL_ENDPOINT_EPISODE, data=data)
    if req.status_code == HTTPStatus.CREATED:
        return req.json()
    return None


def create_serie_remote(serie):
    serie_remote = has_object(serie, URL_ENDPOINT_SERIE)
    if not serie_remote:
        data = {
            "id": str(serie.id),
            "title": str(serie.title),
            "image": str(serie.image),
            "year": str(serie.year),
            "rating": str(serie.rating),
            "url": str(serie.url)
        }
        req = requests.post(URL_ENDPOINT_SERIE, data=data)
        if req.status_code == HTTPStatus.CREATED:
            return req.json()
        else:
            print('Err ao criar serie no Server')
            return None
    else:
        return serie_remote
