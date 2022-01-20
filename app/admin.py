#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.contrib import admin

from app.models import *


# Register your models here.


def approve_selected(modeladmin, request, queryset):
    queryset.update(is_approved=True)


def desapprove_selected(modeladmin, request, queryset):
    queryset.update(is_approved=False)


approve_selected.short_description = "Aprovar itens selecionados"
desapprove_selected.short_description = "Desaprovar itens selecionados"


class MovieAdmin(admin.ModelAdmin):
    list_filter = []
    search_fields = (
        'id',
    )
    inlines = []
    list_display = ("id", "title", "year", "rating", "image", "url", "link_m3u8")


admin.site.register(Movie, MovieAdmin)


class EpisodioInline(admin.TabularInline):
    model = Episodio


class SerieAdmin(admin.ModelAdmin):
    list_filter = []
    search_fields = (
        'id',
    )
    inlines = [EpisodioInline, ]
    list_display = ("id", "title", "year", "rating", "image", "url")


admin.site.register(Serie, SerieAdmin)


class ChannelAdmin(admin.ModelAdmin):
    list_filter = []
    search_fields = (
        'id',
    )
    inlines = []
    list_display = ("id", "title", "image", "category", "url", "link_m3u8")


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


class EpisodioAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'url', 'link_m3u8']


admin.site.register(Episodio, EpisodioAdmin)
