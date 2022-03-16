#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import time
from http import HTTPStatus

import requests
from bs4 import BeautifulSoup
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse, HttpResponse, HttpResponseNotFound
from django.shortcuts import redirect
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

from app.epg.builder import builder_file
from app.epg.core import collect_all
from app.templatetags.form_utils import calc_prazo
from app.views.megapack import MegaPack

try:
    from django.core.urlresolvers import reverse_lazy
except ImportError:
    from django.urls import reverse_lazy, reverse

from app.models import Channel, Category
from app.mixins import ChannelMixin

from app.utils import get_articles, get_program_content, remove_iv

import django_filters


class ChannelFilter(django_filters.FilterSet):
    class Meta:
        model = Channel
        fields = ["id", "title", "image", "url"]


class List(LoginRequiredMixin, ChannelMixin, ListView):
    """
    List all Channels
    """
    login_url = '/admin/login/'
    template_name = 'channel/list.html'
    model = Channel
    ordering = 'title'
    context_object_name = 'channels'


class Detail(LoginRequiredMixin, ChannelMixin, DetailView):
    """
    Detail of a Channel
    """
    login_url = '/admin/login/'
    model = Channel
    template_name = 'channel/detail.html'
    context_object_name = 'channel'

    def is_in(self, a_list, index):
        if index >= 0:
            return index < len(a_list)
        return False

    def get_context_data(self, **kwargs):
        # print('---- Run CRON JOB my_cron_job')
        # req = get_m3u8_channels({})
        # print(req)
        context = super(Detail, self).get_context_data(**kwargs)
        channel = self.get_object()
        context['list_category'] = Channel.objects.filter(category=channel.category).order_by('title')
        channels_list = [channel_obj.id for channel_obj in Channel.objects.all().order_by('title')]
        index_channel = channels_list.index(channel.id)
        next_index = index_channel + 1
        previous_index = index_channel - 1
        if self.is_in(channels_list, next_index):
            context['next_channel'] = Channel.objects.get(id=channels_list[next_index])
        if self.is_in(channels_list, previous_index):
            context['previous_channel'] = Channel.objects.get(id=channels_list[previous_index])
        return context


def delete_all_channels(request):
    Channel.objects.all().delete()
    return redirect('CHANNEL_list')


def get_channels(request):
    url_channels = 'https://megafilmeshdd.org/categoria/canais/page/{}'

    def title_exists(title):
        qs = Channel.objects.filter(title=title)
        if qs.exists():
            return qs.first()
        return None

    def updator():
        print('-')

    def save_channel(title, rating, image, data_lancamento, url_channel):
        channel = Channel()
        channel.title = title
        channel.image = image
        channel.category = Category.objects.first()
        channel.url = url_channel
        mega = MegaPack()
        try:
            dic_m3u8 = mega.get_info(url_channel)
            channel.link_m3u8 = dic_m3u8['m3u8']
            # channel.code = dic_m3u8['code']
            channel.save()
            print('--- canal salvo: ' + str(channel.title))
        except (Exception,):
            channel.link_m3u8 = None
            channel.save()
            print('--- err ao coletar link m3u8: ' + str(channel.title))

    return get_articles(url_channels, 5, {'class': 'items'}, save_channel, title_exists, updator)


def get_content_url(request):
    id = request.GET['id']
    channel = Channel.objects.get(id=id)
    return JsonResponse({'content': get_program_content(channel.program.url)})


def get_m3u8_channels(request, mega=None):
    # remove_older_program_day()
    # collect_all()
    # builder_file()
    if not mega:
        mega = MegaPack()
    return get_m3u8_sinal_publico(request, mega)
    # return get_m3u8_megahdd_default(request, mega)


def get_m3u8_megahdd_default(request, mega: MegaPack = None):
    if not mega:
        mega = MegaPack()
    print(time.asctime())
    channels = Channel.objects.all().order_by('title')
    for channel in channels:
        print('-- ', channel.title)
        try:
            dic_m3u8 = mega.get_info(channel.url)
            channel.link_m3u8 = dic_m3u8['m3u8']
            # channel.code = dic_m3u8['code']
            channel.custom_m3u8 = get_custom_m3u8_local(channel)
            channel.save()
        except (Exception,):
            channel.link_m3u8 = None
            channel.save()
            print('--- err ao coletar link m3u8: ' + str(channel.title))
    print(time.asctime())
    return JsonResponse({'message': 'ok'})


def get_m3u8_sinal_publico(request, mega: MegaPack = None):
    if not mega:
        mega = MegaPack()
    print(time.asctime())
    channels = Channel.objects.all().order_by('title')
    for channel in channels:
        url = 'view-source:http://sinalpublico.com/player3/ch.php?canal={}'
        print('-- ', channel.title)
        try:
            dic_m3u8 = mega.get_info_sinal_publico(url.format(channel.code))
            channel.link_m3u8 = dic_m3u8['m3u8']
            while(not calc_prazo(channel.link_m3u8)):
                dic_m3u8 = mega.get_info_sinal_publico(url.format(channel.code))
                channel.link_m3u8 = dic_m3u8['m3u8']
                print(dic_m3u8['m3u8'])
                # channel.code = dic_m3u8['code']
            channel.custom_m3u8 = get_custom_m3u8_local(channel)
            channel.save()
        except (Exception,):
            channel.link_m3u8 = None
            channel.save()
            print('--- err ao coletar link m3u8: ' + str(channel.title))
    print(time.asctime())
    return JsonResponse({'message': 'ok'})


def get_custom_m3u8_local(channel):
    return '/multi/playlist.m3u8?id={}'.format(str(channel.id))


def update_m3u8_channel(request, id):
    channel = Channel.objects.get(id=id)

    url = 'view-source:http://sinalpublico.com/player3/ch.php?canal={}'
    mega = MegaPack()
    try:
        dic_m3u8 = mega.get_info_sinal_publico(url.format(channel.code))
        channel.link_m3u8 = dic_m3u8['m3u8']
        # channel.code = dic_m3u8['code']
        channel.custom_m3u8 = get_custom_m3u8_local(channel)
        channel.save()
    except (Exception,):
        channel.link_m3u8 = None
        channel.save()
        print('--- err ao coletar link m3u8: ' + str(channel.title))
    mega.close()
    return JsonResponse({'message': 'updated'})


def check_m3u8(channel):
    link = channel.link_m3u8
    prazo = calc_prazo(link)
    if not prazo:
        update_m3u8_channel({}, channel.id)
        return channel.link_m3u8
    return link


HEADERS = {'origin': 'https://sinalpublico.com', 'referer': 'https://sinalpublico.com/',
           'Accept': '*/*',
           'Accept-Encoding': 'gzip, deflate, br',
           'Accept-Language': 'pt-BR, pt;q=0.9, en-US;q=0.8, en;q=0.7',
           'Cache-Control': 'no-cache',
           'Connection': 'keep - alive',
           'Sec-Fetch-Dest': 'empty',
           'Sec-Fetch-Mode': 'cors',
           'Sec-Fetch-Site': 'cross-site',
           'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'}


def playlist_m3u8(request):
    dic = dict(request.GET)
    id = dic['id'][0]
    channel = Channel.objects.get(id=id)
    uri_m3u8 = check_m3u8(channel)
    req = requests.get(url=uri_m3u8, headers=HEADERS, verify=False, timeout=(1, 27))
    page = BeautifulSoup(req.text, 'html.parser')
    page_str = str(page.contents[0])
    arr_strings = list(set(remove_iv(re.findall("([^\s]+.ts)", page_str))))
    if len(arr_strings) > 0:
        for i in range(len(arr_strings)):
            new_uri = arr_strings[i]
            page_str = page_str.replace(arr_strings[i],
                                        'http://' + request.META['HTTP_HOST'] + '/multi/ts?link=' + str(
                                            new_uri))
    return HttpResponse(
        content=page_str,
        status=req.status_code,
        content_type=req.headers['Content-Type']
    )


def get_ts(request):
    key = request.GET['link']
    req = requests.get(url=key, stream=True, timeout=(1, 27), headers=HEADERS, verify=False)
    if req.status_code == 200:
        return HttpResponse(
            content=req.content,
            status=req.status_code,
            content_type=req.headers['Content-Type']
        )
    else:
        return HttpResponseNotFound("hello")


def generate_lista_formatted(request):
    f = open("lista2.m3u8", "a")
    f.truncate(0)
    f.write("#EXTM3U\n")
    for ch in Channel.objects.filter(link_m3u8__icontains='.m3u8').distinct().order_by('title'):
        title = ch.title
        id = ch.id
        custom_m3u8 = 'http://' + request.META['HTTP_HOST'] + '/multi/playlist.m3u8?id=' + str(ch.id)
        f.write('#EXTINF:{}, tvg-id="{} - {}" tvg-name="{} - {}" tvg-logo="{}" group-title="{}",{}\n{}\n'.format(
            '-1',
            id,
            title,
            title,
            id,
            ch.image,
            str(ch.category.name),
            title,
            custom_m3u8))
    f.close()
    fsock = open("lista2.m3u8", "rb")
    return HttpResponse(fsock, content_type='text')


def generate_lista_default(request):
    f = open("lista.m3u8", "a")
    f.truncate(0)
    f.write("#EXTM3U\n")
    for ch in Channel.objects.filter(link_m3u8__icontains='.m3u8').distinct().order_by('title'):
        title = ch.title
        custom_m3u8 = 'http://' + request.META['HTTP_HOST'] + '/multi/playlist.m3u8?id=' + str(ch.id)
        f.write('#EXTINF:{}, tvg-id="{} - {}" tvg-name="{} - {}" tvg-logo="{}" group-title="{}",{}\n{}\n'.format(
            ch.id,
            ch.id,
            title,
            title,
            ch.id,
            ch.image,
            'Canais Ao Vivo',
            title,
            custom_m3u8))
    f.close()
    fsock = open("lista.m3u8", "rb")
    return HttpResponse(fsock, content_type='text')


def generate_epg(request):
    collect_all()
    builder_file()
    return JsonResponse({'message': 'ok'})


def get_epg(request):
    fsock = open("epg.xml", "rb")
    return HttpResponse(fsock, content_type='application/xml')


def updator():
    for channel in Channel.objects.all().order_by('title'):
        ch_server = has_channel(channel)
        if ch_server:
            data = {
                'id': str(channel.id),
                'image': str(channel.image),
            }
            obj_updated = update_channel_remote(ch_server, data)
            if not obj_updated:
                print('Not Updated: ' + str(channel.title))
            else:
                print('Updated: ' + str(channel.title))
        else:
            obj_created = create_channel_remote(channel)
            if obj_created:
                print('Created new channel: ' + str(channel.title))


URL_ENDPOINT = 'https://megafilmes.herokuapp.com/api/channel/'


def has_channel(channel):
    req = requests.get(URL_ENDPOINT + '?title=' + channel.title).json()
    if req:
        return req[0]
    return None


def update_channel_remote(olddata, newdata):
    req = requests.patch(URL_ENDPOINT + str(olddata['id']) + '/', data=newdata)
    if req.status_code == 200:
        return req.json()
    return None


def create_channel_remote(channel):
    data = {
        "id": str(channel.id),
        "title": str(channel.title),
        "image": str(channel.image),
        "code": str(channel.code),
        "url": str(channel.url),
        "link_m3u8": str(channel.link_m3u8),
        "custom_m3u8": str(channel.custom_m3u8)
    }
    req = requests.post(URL_ENDPOINT, data=data)
    if req.status_code == HTTPStatus.CREATED:
        return req.json()
    return None
