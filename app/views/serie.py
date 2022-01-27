#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unidecode
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

from app.templatetags.form_utils import calc_prazo
from app.views.megapack import MegaPack
from app.views.movie import remove_accents

try:
    from django.core.urlresolvers import reverse_lazy
except ImportError:
    from django.urls import reverse_lazy, reverse

from app.models import Serie, Playlist, UrlPlaylist, Episodio
from app.mixins import SerieMixin

from django_datatables_view.base_datatable_view import BaseDatatableView

from app.utils import get_articles, get_page

import django_filters


class SerieFilter(django_filters.FilterSet):
    class Meta:
        model = Serie
        fields = ["title", "year", "rating",]


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


def check_url_assistido(serie, url):
    for p in serie.playlist_set.all():
        for u in p.urlplaylist_set.all():
            if u.url == url:
                return True
    return False


def get_episodes(object):
    page = get_page(object.url, {})
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
        new_link = get_m3u8_episodio(self.request, self.get_object(), search=True)
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
        get_episodes(serie)

    return get_articles(url_series, 50, {'id': 'archive-content'}, save_serie, title_exists)


def get_m3u8_episodio(request, episodio, search=False):
    if episodio.link_m3u8:
        if calc_prazo(episodio.link_m3u8):
            return episodio.link_m3u8
    if search:
        url_m3u8 = MegaPack(episodio.url).get_info()
        episodio.link_m3u8 = url_m3u8
        episodio.save()
        return url_m3u8
    return 'http://' + request.META['HTTP_HOST'] + '/serie/playlist.m3u8?id=' + str(episodio.id)


def generate_selected_episodes(request):
    ids = request.GET.getlist('ids')
    f = open("episode-selected.m3u8", "a")
    f.truncate(0)
    f.write("#EXTM3U\n")
    for id in ids:
        episode = Episodio.objects.get(id=id)
        title = unidecode.unidecode(remove_accents(episode.title))
        uri_m3u8 = get_m3u8_episodio(request, episode, search=True)
        f.write('#EXTINF:{}, tvg-id="{} - {}" tvg-name="{} - {}" tvg-logo="{}" group-title="{}",{}\n{}\n'.format(
            episode.id,
            episode.id,
            title,
            title,
            episode.id,
            episode.image,
            'Episodes',
            title,
            uri_m3u8))
    f.close()
    return JsonResponse({'message': 'ok'})


def get_episodes_m3u8(request):
    fsock = open("episode-selected.m3u8", "rb")
    return HttpResponse(fsock, content_type='text')
