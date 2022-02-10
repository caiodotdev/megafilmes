#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.contrib import admin

from app.models import *
# Register your models here.
from app.views.megapack import MegaPack
from app.views.movie import get_m3u8_movies, write_m3u8_movies, updator_movies_server
from app.views.serie import write_m3u8_series, get_m3u8_episodes, updator_series_server


def approve_selected_movies(modeladmin, request, queryset):
    queryset.update(selected=True)
    mega = MegaPack()
    get_m3u8_movies({}, mega=mega)
    mega.close()
    write_m3u8_movies()
    updator_movies_server()


def desapprove_selected_movies(modeladmin, request, queryset):
    queryset.update(selected=False)
    write_m3u8_movies()
    updator_movies_server()


approve_selected_movies.short_description = "Selecionar FILMES selecionados"
desapprove_selected_movies.short_description = "Remover Selected dos FILMES"


def approve_selected_series(modeladmin, request, queryset):
    queryset.update(selected=True)
    mega = MegaPack()
    get_m3u8_episodes({}, mega=mega)
    mega.close()
    write_m3u8_series()
    updator_series_server()


def desapprove_selected_series(modeladmin, request, queryset):
    queryset.update(selected=False)
    write_m3u8_series()
    updator_series_server()


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
    search_fields = ['serie__title', ]
    list_display = ['id', 'title', "serie", "selected", 'url', 'link_m3u8']
    actions = [approve_selected_series, desapprove_selected_series, ]


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
    list_display = ("id", "title", "code", "category", "program_url", "link_m3u8", "url", "image",)


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


class ProgramItemInline(admin.TabularInline):
    model = ProgramItem


class ProgramDayAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'channel']
    inlines = [ProgramItemInline, ]


class ProgramItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'subtitle', 'program_day', 'hour', 'hour_formatted', 'start', 'stop', ]


class SourceAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'source', 'image']


admin.site.register(ProgramDay, ProgramDayAdmin)
admin.site.register(ProgramItem, ProgramItemAdmin)
admin.site.register(Source, SourceAdmin)
