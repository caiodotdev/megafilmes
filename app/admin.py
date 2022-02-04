#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.contrib import admin

from app.models import *
# Register your models here.
from app.views.movie import get_m3u8_movies, write_m3u8_movies
from app.views.serie import write_m3u8_series


def approve_selected_movies(modeladmin, request, queryset):
    queryset.update(selected=True)
    get_m3u8_movies({})
    write_m3u8_movies()


def desapprove_selected_movies(modeladmin, request, queryset):
    queryset.update(selected=False)
    write_m3u8_movies()


approve_selected_movies.short_description = "Selecionar FILMES selecionados"
desapprove_selected_movies.short_description = "Remover Selected dos FILMES"


def approve_selected_series(modeladmin, request, queryset):
    queryset.update(selected=True)
    get_m3u8_movies({})
    write_m3u8_series()


def desapprove_selected_series(modeladmin, request, queryset):
    queryset.update(selected=False)
    write_m3u8_series()


approve_selected_series.short_description = "Selecionar EPISODIOS selecionados"
desapprove_selected_series.short_description = "Remover Selected dos EPISODIOS"


class MovieAdmin(admin.ModelAdmin):
    list_filter = []
    search_fields = (
        'title',
    )
    inlines = []
    list_display = ("id", "selected", "title", "year", "rating", "link_m3u8", "url", "image",)
    actions = [approve_selected_movies, desapprove_selected_movies, ]


admin.site.register(Movie, MovieAdmin)


class EpisodioInline(admin.TabularInline):
    model = Episodio


class EpisodioAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', "selected", 'url', 'link_m3u8']


admin.site.register(Episodio, EpisodioAdmin)


class SerieAdmin(admin.ModelAdmin):
    list_filter = []
    search_fields = (
        'title',
    )
    inlines = [EpisodioInline, ]
    list_display = ("id", "title", "year", "rating", "image", "url")


admin.site.register(Serie, SerieAdmin)


class ChannelAdmin(admin.ModelAdmin):
    list_filter = []
    search_fields = (
        'title',
    )
    inlines = []
    list_display = ("id", "title", "code", "category", "link_m3u8", "url", "image",)


admin.site.register(Channel, ChannelAdmin)


class LinkAdmin(admin.ModelAdmin):
    list_display = ['id', 'm3u8', 'url']


admin.site.register(LinkChannel, LinkAdmin)


class UrlPlaylistInline(admin.TabularInline):
    model = UrlPlaylist


class PlaylistAdmin(admin.ModelAdmin):
    list_display = ['id', 'titulos', 'serie']
    inlines = [UrlPlaylistInline, ]


admin.site.register(Playlist, PlaylistAdmin)


class UrlPlaylistAdmin(admin.ModelAdmin):
    list_display = ['id', 'playlist', 'url']


admin.site.register(UrlPlaylist, UrlPlaylistAdmin)


class ChannelInline(admin.TabularInline):
    model = Channel


class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    inlines = [ChannelInline, ]


admin.site.register(Category, CategoryAdmin)
