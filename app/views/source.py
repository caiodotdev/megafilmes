from http import HTTPStatus

import django_filters
import requests
from django.db.models import Q
from django.views.generic import ListView, DetailView
from django_common.mixin import LoginRequiredMixin
from django_datatables_view.base_datatable_view import BaseDatatableView

from app.mixins import SourceMixin
from app.models import Source


class SourceFilter(django_filters.FilterSet):
    class Meta:
        model = Source
        fields = ["id", "title", "image", "source"]


class List(LoginRequiredMixin, SourceMixin, ListView):
    """
    List all Sources
    """
    login_url = '/admin/login/'
    template_name = 'source/list.html'
    model = Source
    queryset = Source.objects.all()
    context_object_name = 'sources'
    ordering = 'id'
    paginate_by = 10
    search = ''

    def get_queryset(self):
        queryset = Source.objects.all()
        filter = SourceFilter(self.request.GET, queryset)
        queryset = self.search_general(filter.qs)
        queryset = self.ordering_data(queryset)
        return queryset

    def search_general(self, qs):
        if 'search' in self.request.GET:
            self.search = self.request.GET['search']
            if self.search:
                search = self.search
                qs = qs.filter(Q(id__icontains=search) | Q(title__icontains=search) |
                               Q(image__icontains=search) | Q(source__icontains=search))
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
        context = super(List, self).get_context_data(**kwargs)
        queryset = self.get_queryset()
        filter = SourceFilter(self.request.GET, queryset)
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


class Detail(LoginRequiredMixin, SourceMixin, DetailView):
    """
    Detail of a Source
    """
    login_url = '/admin/login/'
    model = Source
    template_name = 'source/detail.html'
    context_object_name = 'source'


class SourceListJson(BaseDatatableView):
    model = Source
    columns = ("id", "image", "title", "source",)
    order_columns = ["id", "image", "title", "source"]
    max_display_length = 500

    def filter_queryset(self, qs):
        search = self.request.GET.get('search[value]', None)
        if search:
            qs = qs.filter(Q(id__icontains=search) | Q(title__icontains=search) | Q(image__icontains=search) | Q(
                source__icontains=search))
        filter = SourceFilter(self.request.GET, qs)
        return filter.qs


def delete_all_sources_server():
    list_sources_server = requests.get(URL_ENDPOINT_SOURCE).json()
    if list_sources_server:
        for source_server in list_sources_server:
            requests.delete(URL_ENDPOINT_SOURCE + source_server['id'] + '/')


def updator_sources_server():
    delete_all_sources_server()
    for source in Source.objects.all():
        source_server = has_source(source)
        if source_server:
            data = {
                "id": str(source.id),
                "title": str(source.title),
                "image": str(source.image),
                "source": str(source.source)
            }
            obj_updated = update_source_remote(source_server, data)
            if not obj_updated:
                print('Not Updated: ' + str(source.title))
            else:
                print('Updated: ' + str(source.title))
        else:
            obj_created = create_source_remote(source)
            if obj_created:
                print('Created new movie: ' + str(source.title))


URL_ENDPOINT_SOURCE = 'https://megafilmes.herokuapp.com/api/source/'


def has_source(movie):
    req = requests.get(URL_ENDPOINT_SOURCE + '?id=' + str(movie.id)).json()
    if req:
        return req[0]
    return None


def update_source_remote(olddata, newdata):
    req = requests.patch(URL_ENDPOINT_SOURCE + str(olddata['id']) + '/', data=newdata)
    if req.status_code == 200:
        return req.json()
    return None


def create_source_remote(source):
    data = {
        "id": str(source.id),
        "title": str(source.title),
        "image": str(source.image),
        "source": str(source.source)
    }
    req = requests.post(URL_ENDPOINT_SOURCE, data=data)
    if req.status_code == HTTPStatus.CREATED:
        return req.json()
    return None
