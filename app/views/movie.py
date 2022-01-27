#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unicodedata
import unidecode
from django.contrib import messages
from django.contrib.admin.utils import NestedObjects
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.views.generic.detail import DetailView
from django.views.generic.edit import (
    DeleteView
)
from django.views.generic.list import ListView

from app.templatetags.form_utils import calc_prazo
from app.views.megapack import MegaPack

try:
    from django.core.urlresolvers import reverse_lazy
except ImportError:
    from django.urls import reverse_lazy, reverse

from app.models import Movie
from app.mixins import MovieMixin
from app.conf import MOVIE_LIST_URL_NAME

from django_datatables_view.base_datatable_view import BaseDatatableView

from app.utils import get_articles

import django_filters


class MovieFilter(django_filters.FilterSet):
    class Meta:
        model = Movie
        fields = ["title", "year", "rating"]


class List(LoginRequiredMixin, MovieMixin, ListView):
    """
    List all Movies
    """
    login_url = '/admin/login/'
    template_name = 'movie/list.html'
    model = Movie
    context_object_name = 'movies'
    paginate_by = 1

    def get_context_data(self, **kwargs):
        context = super(List, self).get_context_data(**kwargs)
        queryset = self.get_queryset()
        filter = MovieFilter(self.request.GET, queryset)
        context["filter"] = filter
        return context


class Detail(LoginRequiredMixin, MovieMixin, DetailView):
    """
    Detail of a Movie
    """
    login_url = '/admin/login/'
    model = Movie
    template_name = 'movie/detail.html'
    context_object_name = 'movie'

    def get_context_data(self, **kwargs):
        context = super(Detail, self).get_context_data(**kwargs)
        mega = MegaPack(self.object.url)
        link = mega.get_info()
        context['m3u8'] = link
        return context


class Delete(LoginRequiredMixin, MovieMixin, PermissionRequiredMixin, DeleteView):
    """
    Delete a Movie
    """
    login_url = '/admin/login/'
    model = Movie
    permission_required = (
        'app.delete_movie'
    )
    template_name = 'movie/delete.html'
    context_object_name = 'movie'

    def get_context_data(self, **kwargs):
        context = super(Delete, self).get_context_data(**kwargs)
        collector = NestedObjects(using='default')
        collector.collect([self.get_object()])
        context['deleted_objects'] = collector.nested()
        return context

    def __init__(self):
        super(Delete, self).__init__()

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Movie removido com sucesso')
        return super(Delete, self).delete(self.request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy(MOVIE_LIST_URL_NAME)


class MovieListJson(BaseDatatableView):
    model = Movie
    columns = ("id", "image", "title", "year", "rating")
    order_columns = ["id", "image", "title", "year", "rating"]
    max_display_length = 500

    def filter_queryset(self, qs):
        search = self.request.GET.get('search[value]', None)
        if search:
            qs = qs.filter(Q(id__icontains=search) | Q(title__icontains=search) | Q(year__icontains=search) | Q(
                rating__icontains=search) | Q(image__icontains=search) | Q(url__icontains=search))
        filter = MovieFilter(self.request.GET, qs)
        return filter.qs


def delete_all_movies(request):
    Movie.objects.all().delete()
    return redirect('MOVIE_list')


def get_movies(request):
    url_movies = 'https://megafilmeshdd.org/filmes/page/{}'

    def title_exists(title):
        return Movie.objects.filter(title=title).exists()

    def save_movie(title, rating, image, data_lancamento, url_movie):
        movie = Movie()
        movie.title = title
        movie.rating = rating
        movie.image = image
        movie.year = data_lancamento
        movie.url = url_movie
        movie.save()

    return get_articles(url_movies, 270, {'id': 'archive-content'}, save_movie, title_exists)


def remove_accents(text):
    if isinstance(text, bytes):
        text = text.decode('ascii')

    category = unicodedata.category  # this gives a small (~10%) speedup
    return ''.join(
        c for c in unicodedata.normalize('NFKD', text) if category(c) != 'Mn'
    )


def get_m3u8_movie(movie):
    url_m3u8 = MegaPack(movie.url).get_info()
    movie.link_m3u8 = url_m3u8
    movie.save()
    return url_m3u8


def generate_selected_movies(request):
    ids = request.GET.getlist('ids')
    f = open("movies-selected.m3u8", "a")
    f.truncate(0)
    f.write("#EXTM3U\n")
    for id in ids:
        movie = Movie.objects.get(id=id)
        title = unidecode.unidecode(remove_accents(movie.title))
        uri_m3u8 = get_m3u8_movie(movie)
        f.write('#EXTINF:{}, tvg-id="{} - {}" tvg-name="{} - {}" tvg-logo="{}" group-title="{}",{}\n{}\n'.format(
            movie.id,
            movie.id,
            title,
            title,
            movie.id,
            movie.image,
            'Filmes',
            title,
            uri_m3u8))
    f.close()
    return JsonResponse({'message': 'ok'})


def get_list_m3u8(request):
    fsock = open("movies-selected.m3u8", "rb")
    return HttpResponse(fsock, content_type='text')
