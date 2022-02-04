import django_filters
import rest_framework.filters
from django_filters import rest_framework as filters
from rest_framework import viewsets

from . import (
    serializers,
    models
)


class MovieFilter(django_filters.FilterSet):
    class Meta:
        model = models.Movie
        fields = ["id", "title", "year", "rating", "image", "url", "selected", "link_m3u8"]


class MovieViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.MovieSerializer
    queryset = models.Movie.objects.all()
    filterset_class = MovieFilter
    filter_backends = (filters.DjangoFilterBackend, rest_framework.filters.SearchFilter,)
    search_fields = ['title',]
    ordering_fields = '__all__'


class SerieFilter(django_filters.FilterSet):
    class Meta:
        model = models.Serie
        fields = ["id", "title", "year", "rating", "image", "url"]


class SerieViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.SerieSerializer
    queryset = models.Serie.objects.all()
    filterset_class = SerieFilter
    filter_backends = (filters.DjangoFilterBackend, rest_framework.filters.SearchFilter,)
    search_fields = ['title', ]
    ordering_fields = '__all__'


class ChannelFilter(django_filters.FilterSet):
    class Meta:
        model = models.Channel
        fields = ["id", "title", "image", "url", "link_m3u8",  "code", "custom_m3u8"]


class ChannelViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.ChannelSerializer
    queryset = models.Channel.objects.all().order_by('title')
    filterset_class = ChannelFilter
    filter_backends = (filters.DjangoFilterBackend, rest_framework.filters.SearchFilter,)
    search_fields = ['title', ]
    ordering_fields = '__all__'
