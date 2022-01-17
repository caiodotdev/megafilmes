from django.urls import path, include
from django.views.generic import TemplateView

from app import conf

from app.urls_api import api_urlpatterns
from app.views.channel import playlist_m3u8, get_ts

urlpatterns = []

urlpatterns += [
    path('', include('rest_auth.urls')),
    path('registration/', include('rest_auth.registration.urls'))
]

from app.views import movie

urlpatterns += [
    # movie
    path(
        '',
        movie.List.as_view(),
        name=conf.MOVIE_LIST_URL_NAME
    ),
    path(
        'movie/full/',
        movie.ListFull.as_view(),
        name='MOVIE_list_full'
    ),
    path(
        'movie/create/',
        movie.Create.as_view(),
        name=conf.MOVIE_CREATE_URL_NAME
    ),
    path(
        'movie/<int:pk>/',
        movie.Detail.as_view(),
        name=conf.MOVIE_DETAIL_URL_NAME
    ),
    path(
        'movie/<int:pk>/update/',
        movie.Update.as_view(),
        name=conf.MOVIE_UPDATE_URL_NAME
    ),
    path(
        'movie/<int:pk>/delete/',
        movie.Delete.as_view(),
        name=conf.MOVIE_DELETE_URL_NAME
    ),
    path(
        'movie/list/json/',
        movie.MovieListJson.as_view(),
        name=conf.MOVIE_LIST_JSON_URL_NAME
    ),
    path(
        'get-movies',
        movie.get_movies,
        name='get_movies'
    ),
    path(
        'delete-movies',
        movie.delete_all_movies,
        name='delete_all_movies'
    ),
    path('filmes.m3u8', movie.gen_lista_movie, name='gen_lista_movies'),
    path('movie/playlist.m3u8', movie.movie_playlist_m3u8, name='movie_playlist_m3u8'),
]

from app.views import serie

urlpatterns += [
    # serie
    path(
        'serie/',
        serie.List.as_view(),
        name=conf.SERIE_LIST_URL_NAME
    ),
    path(
        'serie/full/',
        serie.ListFull.as_view(),
        name='SERIE_list_full'
    ),
    path(
        'serie/create/',
        serie.Create.as_view(),
        name=conf.SERIE_CREATE_URL_NAME
    ),
    path(
        'serie/<int:pk>/',
        serie.Detail.as_view(),
        name=conf.SERIE_DETAIL_URL_NAME
    ),
    path(
        'serie/episode/',
        serie.Episode.as_view(),
        name='SERIE_episode'
    ),
    path(
        'serie/<int:pk>/update/',
        serie.Update.as_view(),
        name=conf.SERIE_UPDATE_URL_NAME
    ),
    path(
        'serie/<int:pk>/delete/',
        serie.Delete.as_view(),
        name=conf.SERIE_DELETE_URL_NAME
    ),
    path(
        'serie/list/json/',
        serie.SerieListJson.as_view(),
        name=conf.SERIE_LIST_JSON_URL_NAME
    ),
    path(
        'get-series',
        serie.get_series,
        name='get_series'
    ),
    path(
        'delete-series',
        serie.delete_all_series,
        name='delete_all_series'
    ),
    path('series.m3u8', serie.gen_lista_serie, name='gen_lista_serie'),
    path('serie/playlist.m3u8', serie.episodio_playlist_m3u8, name='episodio_playlist_m3u8')
]

from app.views import channel

urlpatterns += [
    # channel
    path(
        'channel/',
        channel.List.as_view(),
        name=conf.CHANNEL_LIST_URL_NAME
    ),
    path(
        'channel/full/',
        channel.ListFull.as_view(),
        name='CHANNEL_list_full'
    ),
    path(
        'channel/create/',
        channel.Create.as_view(),
        name=conf.CHANNEL_CREATE_URL_NAME
    ),
    path(
        'channel/<int:pk>/',
        channel.Detail.as_view(),
        name=conf.CHANNEL_DETAIL_URL_NAME
    ),
    path(
        'channel/<int:pk>/update/',
        channel.Update.as_view(),
        name=conf.CHANNEL_UPDATE_URL_NAME
    ),
    path(
        'channel/<int:pk>/delete/',
        channel.Delete.as_view(),
        name=conf.CHANNEL_DELETE_URL_NAME
    ),
    path(
        'channel/list/json/',
        channel.ChannelListJson.as_view(),
        name=conf.CHANNEL_LIST_JSON_URL_NAME
    ),
    path(
        'get-channels',
        channel.get_channels,
        name='get_channels'
    ),
    path(
        'delete-channels',
        channel.delete_all_channels,
        name='delete_all_channels'
    ),
    path(
        'get-content-url',
        channel.get_content_url,
        name='get_content_url'
    ),
    path(
        'get-channels-m3u8',
        channel.get_m3u8_channels,
        name='get_channels_m3u8'
    ),
    path(
        'get-m3u8-channel/<int:id>/',
        channel.update_m3u8_channel,
        name='get_m3u8_channel'
    ),
    path(
        'lista.m3u8',
        channel.gen_lista,
        name='gen_lista'
    ),
    path(
        'lista2.m3u8',
        channel.gen_lista_personal,
        name='gen_lista_personal'
    ),
    path('multi/playlist.m3u8', playlist_m3u8, name='playlist_m3u8'),
    path('multi/ts', get_ts, name='get_ts'),
    path('loaderio-7366a7cb37fc04bf49ac6c48e3fdcd9f.txt',
         TemplateView.as_view(template_name='channel/loaderio-7366a7cb37fc04bf49ac6c48e3fdcd9f.txt',
                              content_type='text/plain')),
    path('loaderio-7366a7cb37fc04bf49ac6c48e3fdcd9f/',
         TemplateView.as_view(template_name='channel/loaderio-7366a7cb37fc04bf49ac6c48e3fdcd9f.txt',
                              content_type='text/plain')),
]

urlpatterns += api_urlpatterns
