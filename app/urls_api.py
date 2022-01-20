from rest_framework.routers import DefaultRouter

from app import (
    viewsets
)

api_urlpatterns = []

movie_router = DefaultRouter()

movie_router.register(
    r'^api/movie',
    viewsets.MovieViewSet,
    basename="movie"
)

api_urlpatterns += movie_router.urls
serie_router = DefaultRouter()

serie_router.register(
    r'^api/serie',
    viewsets.SerieViewSet,
    basename="serie"
)

api_urlpatterns += serie_router.urls
channel_router = DefaultRouter()

channel_router.register(
    r'^api/channel',
    viewsets.ChannelViewSet,
    basename="channel"
)

api_urlpatterns += channel_router.urls
