#!/usr/bin/env python
# -*- coding: utf-8 -*-
from http import HTTPStatus

import requests
import unicodedata
import unidecode
from django.contrib import messages
from django.contrib.admin.utils import NestedObjects
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db import transaction
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


class MovieFormSetManagement(object):
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
        return super(MovieFormSetManagement, self).form_valid(form)

    def get_context_data(self, **kwargs):
        data = super(MovieFormSetManagement, self).get_context_data(**kwargs)
        for Formset in self.formsets:
            if self.request.POST:
                data["{}set".format(str(Formset.model.__name__).lower())] = Formset(self.request.POST,
                                                                                    self.request.FILES,
                                                                                    instance=self.object)
            else:
                data["{}set".format(str(Formset.model.__name__).lower())] = Formset(instance=self.object)
        return data


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


class ListSelected(LoginRequiredMixin, MovieMixin, ListView):
    """
    List all Movies
    """
    login_url = '/admin/login/'
    template_name = 'movie/list_selected.html'
    model = Movie
    queryset = Movie.objects.filter(selected=True)
    context_object_name = 'movies'
    ordering = '-id'
    paginate_by = 10
    search = ''

    def get_queryset(self):
        queryset = Movie.objects.filter(selected=True)
        filter = MovieFilter(self.request.GET, queryset)
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
        context = super(ListSelected, self).get_context_data(**kwargs)
        queryset = self.get_queryset()
        filter = MovieFilter(self.request.GET, queryset)
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
        mega = MegaPack()
        dic_m3u8 = mega.get_info(self.object.url)
        context['m3u8'] = dic_m3u8['m3u8']
        mega.close()
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


def generate_selected_movies(request):
    if 'ids' in request.GET:
        ids = request.GET.getlist('ids')
        for id in ids:
            movie = Movie.objects.get(id=id)
            movie.selected = True
            movie.link_m3u8 = MegaPack().get_info(movie.url)['m3u8']
            movie.save()
    write_m3u8_movies()
    return JsonResponse({'message': 'ok'})


def write_m3u8_movies():
    f = open("movies-selected.m3u8", "a")
    f.truncate(0)
    f.write("#EXTM3U\n")
    for movie in Movie.objects.filter(selected=True):
        title = unidecode.unidecode(remove_accents(movie.title))
        f.write('#EXTINF:{}, tvg-id="{} - {}" tvg-name="{} - {}" tvg-logo="{}" group-title="{}",{}\n{}\n'.format(
            movie.id,
            movie.id,
            title,
            title,
            movie.id,
            movie.image,
            'Filmes',
            title,
            movie.link_m3u8))
    f.close()


def get_list_m3u8(request):
    write_m3u8_movies()
    fsock = open("movies-selected.m3u8", "rb")
    return HttpResponse(fsock, content_type='text')


def get_m3u8_movies(request, mega: MegaPack = None):
    if not mega:
        mega = MegaPack()
    movies = Movie.objects.filter(selected=True)
    for movie in movies:
        print('-- ', movie.title)
        try:
            movie.link_m3u8 = mega.get_info(movie.url)['m3u8']
            movie.save()
        except (Exception,):
            movie.link_m3u8 = None
            movie.save()
            print('--- err ao coletar link m3u8: ' + str(movie.title))
    return JsonResponse({'message': 'ok'})


def delete_all_movies_server():
    list_movies_server = requests.get(URL_ENDPOINT_MOVIE).json()
    if list_movies_server:
        for movie_server in list_movies_server:
            requests.delete(URL_ENDPOINT_MOVIE + movie_server['id'] + '/')


def updator_movies_server():
    delete_all_movies_server()
    for movie in Movie.objects.filter(selected=True):
        movie_server = has_movie(movie)
        if movie_server:
            data = {
                "id": str(movie.id),
                "image": str(movie.image),
                "url": str(movie.url),
                "link_m3u8": str(movie.link_m3u8),
                "selected": True
            }
            obj_updated = update_movie_remote(movie_server, data)
            if not obj_updated:
                print('Not Updated: ' + str(movie.title))
            else:
                print('Updated: ' + str(movie.title))
        else:
            obj_created = create_movie_remote(movie)
            if obj_created:
                print('Created new movie: ' + str(movie.title))


URL_ENDPOINT_MOVIE = 'https://megafilmes.herokuapp.com/api/movie/'


def has_movie(movie):
    req = requests.get(URL_ENDPOINT_MOVIE + '?id=' + str(movie.id)).json()
    if req:
        return req[0]
    return None


def update_movie_remote(olddata, newdata):
    req = requests.patch(URL_ENDPOINT_MOVIE + str(olddata['id']) + '/', data=newdata)
    if req.status_code == 200:
        return req.json()
    return None


def create_movie_remote(movie):
    data = {
        "id": str(movie.id),
        "title": str(movie.title),
        "image": str(movie.image),
        "year": str(movie.year),
        "url": str(movie.url),
        "link_m3u8": str(movie.link_m3u8),
        "selected": True
    }
    req = requests.post(URL_ENDPOINT_MOVIE, data=data)
    if req.status_code == HTTPStatus.CREATED:
        return req.json()
    return None
