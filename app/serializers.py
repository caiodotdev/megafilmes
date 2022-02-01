from rest_framework import serializers

from app.models import Movie


class MovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = ("id", "title", "year", "rating", "image", "url", "selected", "link_m3u8")


from app.models import Serie


class SerieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Serie
        fields = ("id", "title", "year", "rating", "image", "url")


from app.models import Channel


class ChannelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Channel
        fields = ("id", "title", "image",  "code", "url", "link_m3u8", "custom_m3u8", "category")
