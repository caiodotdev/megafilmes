from rest_framework import viewsets

from django_filters import rest_framework as filters

from . import (
    serializers,
    models
)

import django_filters


class MovieFilter(django_filters.FilterSet):
    class Meta:
        model = models.Movie
        fields = ["id", "title", "year", "rating", "image", "url"]


class MovieViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.MovieSerializer
    queryset = models.Movie.objects.all()
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = MovieFilter


class SerieFilter(django_filters.FilterSet):
    class Meta:
        model = models.Serie
        fields = ["id", "title", "year", "rating", "image", "url"]


class SerieViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.SerieSerializer
    queryset = models.Serie.objects.all()
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = SerieFilter


class ChannelFilter(django_filters.FilterSet):
    class Meta:
        model = models.Channel
        fields = ["id", "title", "image", "url", "link_m3u8"]


class ChannelViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.ChannelSerializer
    queryset = models.Channel.objects.all()
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = ChannelFilter
